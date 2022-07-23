import sys
import ast
import numpy as np
import pandas as pd
import timeit
from termcolor import colored, cprint
from sklearn.model_selection import StratifiedKFold
from tqdm import tqdm
from fim import apriori, eclat, fpgrowth
from spinner import Spinner
from .utils import *
from .qualification import *
from .rules import *
from models.utils import balanced_dataset
import logging
#-----------------------------------------------------------------------

step_dict = {
    "rules_generate": 0,
    "rules_intersection": 1,
    "rules_superset": 2,
    "rules_subset": 3,
    "rules_qualify": 4,
    "test_apps": 5,
    "results_calc": 6,
    "finished": 7
}

def execute_fim(parameters):
    dataset = parameters[0]
    args = parameters[1]
    algorithm = args.algorithm
    max_l = args.max_length
    dataset_type = parameters[2]
    support = parameters[3] * 100
    confidence = parameters[4] * 100
    report = 'scl'
    str_list = ["Running FIM: Generating", dataset_type, "Association Rules.",
                    "Sup >> {:.2f}".format(support),
                    "Conf >> {:.2f}".format(confidence)]
    info = ' '.join(str_list)
    logger.info(info)
    algorithm_fim = globals()[algorithm]
    result = algorithm_fim(dataset, target = 'r', zmin = 2, zmax = max_l,
                    supp = support, conf = confidence, report = report, mode = 'o')
    r = to_pandas_dataframe(result, report)
    r = generate_unique_rules(r, args.min_lift)

    pct = (1.0 - (len(r)/len(result))) * 100.0 if len(result) != 0 else 0.0
    str_list = ["Generate {}".format(len(r)), dataset_type, "Association Rules ({:.3f})".format(pct)]
    info = ' '.join(str_list)
    logger.info(info)
    return r

def rules_subset(rule_to_check, const_parameters):
    rules_list = const_parameters
    is_subset = any(set(rule_to_check).issubset(r) for r in rules_list)
    if not is_subset:
        return rule_to_check
    return None

def rules_superset(rule_to_check, const_parameters):
    rules_list = const_parameters[0]
    rules_list.remove(rule_to_check)
    args = const_parameters[1]
    max_l = args.max_length
    if len(rule_to_check) == 2:
        return rule_to_check
    for i in range(3, max_l + 1):
        minors_rules = [r for r in rules_list if len(r) < i]
        is_superset = any(set(rule_to_check).issuperset(r) for r in minors_rules)
        if is_superset:
            return None
    return rule_to_check

def get_rules(train, args, fold_no):
    global DIR_BASE
    step = file_content(DIR_BASE, fold_no, "log")
    step = step if len(step) else "rules_generate"
    stopped_step = step_dict.get(step)

    step = "finished"
    if stopped_step == step_dict.get(step):
        mw_rules, bw_rules, time_l = load_data(DIR_BASE, fold_no, stopped_step)
        return mw_rules, bw_rules, time_l

    mw_rules = []
    bw_rules = []
    time_l = []
    step = "rules_generate"
    if stopped_step == step_dict.get(step):
        update_log(DIR_BASE, fold_no, step)
        mw_dataset = train[(train['class'] == 1)]
        mw_dataset = mw_dataset.drop(['class'], axis=1)
        bw_dataset = train[(train['class'] == 0)]
        bw_dataset = bw_dataset.drop(['class'], axis=1)

        logger.info('Preparing MALWARES Data')
        dataset_list = mw_dataset.values.tolist()
        mw_fim = to_fim_format(dataset_list)
        logger.info('Preparing BENIGNS Data')
        dataset_list = bw_dataset.values.tolist()
        bw_fim = to_fim_format(dataset_list)

        mw_sup = args.min_support
        bw_sup = args.min_support
        mw_conf = args.min_confidence
        bw_conf = args.min_confidence

        if not args.use_balanced_datasets:
            if args.use_proportional_values:
                if len(mw_dataset) > len(bw_dataset): #More Malwares Samples
                    sup_factor = len(mw_dataset)/len(bw_dataset)
                    mw_sup = args.min_support * sup_factor
                else: #More Benigns Samples
                    sup_factor = len(bw_dataset)/len(mw_dataset)
                    bw_sup = args.min_support * sup_factor
                mw_conf = len(mw_dataset)/len(train)
                mw_conf = args.min_confidence if args.min_confidence > mw_conf else mw_conf
                bw_conf = len(bw_dataset)/len(train)
                bw_conf = args.min_confidence if args.min_confidence > bw_conf else bw_conf

        p = np.array([[mw_fim, args, "MALWARES", mw_sup, mw_conf], [bw_fim, args, "BENIGNS", bw_sup, bw_conf]], dtype=object)

        start = timeit.default_timer()
        rules = parallelize_func(execute_fim, p, cores = 2)
        end = timeit.default_timer()
        time_tuple = (step, end - start)
        time_l.append(time_tuple)
        mw_rules = rules[0]
        bw_rules = rules[1]
        save_data(mw_rules, bw_rules, time_l, DIR_BASE, fold_no)

    rules = []
    step = "rules_intersection"
    if stopped_step == step_dict.get(step):
        mw_rules, bw_rules, time_l = load_data(DIR_BASE, fold_no, stopped_step)

    if stopped_step <= step_dict.get(step):
        update_log(DIR_BASE, fold_no, step)
        logger.info("Generating Unique Rules: INTERSECTION.")

        start = timeit.default_timer()
        rules_inter = rules_intersection(mw_rules, bw_rules)
        mw_rules = rules_difference(mw_rules, rules_inter)
        bw_rules = rules_difference(bw_rules, rules_inter)
        end = timeit.default_timer()
        time_tuple = (step, end - start)
        time_l.append(time_tuple)
        save_data(mw_rules, bw_rules, time_l, DIR_BASE, fold_no)

    step = "rules_superset"
    if stopped_step == step_dict.get(step):
        mw_rules, bw_rules, time_l = load_data(DIR_BASE, fold_no, stopped_step)

    if stopped_step <= step_dict.get(step):
        update_log(DIR_BASE, fold_no, step)

        start = timeit.default_timer()
        mw_rules = list(mw_rules)
        logger.info("Generating MALWARES Unique Rules: SUPERSET.")
        mw_result = parallelize_func(rules_superset, mw_rules, const_parameters = [mw_rules, args])
        mw_rules = list(filter(None, mw_result))
        bw_rules = list(bw_rules)
        logger.info("Generating BENIGNS Unique Rules: SUPERSET.")
        bw_result = parallelize_func(rules_superset, bw_rules, const_parameters = [bw_rules, args])
        bw_rules = list(filter(None, bw_result))
        end = timeit.default_timer()
        time_tuple = (step, end - start)
        time_l.append(time_tuple)

        save_data(mw_rules, bw_rules, time_l, DIR_BASE, fold_no)

    step = "rules_subset"
    if stopped_step == step_dict.get(step):
        mw_rules, bw_rules, time_l = load_data(DIR_BASE, fold_no, stopped_step)

    if stopped_step <= step_dict.get(step):
        update_log(DIR_BASE, fold_no, step)

        start = timeit.default_timer()
        mw_rules = list(mw_rules)
        logger.info("Generating MALWARES Unique Rules: SUBSET.")
        mw_result = parallelize_func(rules_subset, mw_rules, const_parameters = bw_rules)
        bw_rules = list(bw_rules)
        logger.info("Generating BENIGNS Unique Rules: SUBSET.")
        bw_result = parallelize_func(rules_subset, bw_rules, const_parameters = mw_rules)
        end = timeit.default_timer()
        time_tuple = (step, end - start)
        time_l.append(time_tuple)
        mw_rules = list(filter(None, mw_result))
        bw_rules = list(filter(None, bw_result))
        save_data(mw_rules, bw_rules, time_l, DIR_BASE, fold_no)

    step = "finished"
    update_log(DIR_BASE, fold_no, step)
    return mw_rules, bw_rules, time_l

def quality_parameters(rule, const_parameters):
    train_dataset = const_parameters[0]
    classification = const_parameters[1]
    features = train_dataset.drop(['class'], axis=1)
    class_ = list(train_dataset['class'])

    rule_coverage = 0 # == p + n
    p = 0
    for i in range(0, len(train_dataset)):
        app_ft = features.values[i,:]
        if len(rule) == app_ft[list(rule)].sum():
            rule_coverage += 1
            if class_[i] == classification:
                p += 1
    n = rule_coverage - p
    return [p, n]

def quality_rules(rule_qfy_parameters, const_parameters):
    #Dictionary For Rules Qualify Measures
    rules_measures = {
        'acc': r_accuracy,
        'cov': r_coverage,
        'prec': r_precision,
        'ls': r_logical_sufficiency,
        'bc': r_bayesian_confirmation,
        'kap': r_kappa,
        "zha": r_zhang,
        'corr': r_correlation,
        'c1': r_c1,
        'c2': r_c2,
        'wl': r_wlaplace,
    }
    train_dataset = const_parameters[0]
    q_measure = const_parameters[1]
    positive_class = const_parameters[2]
    D = int(len(train_dataset) * 0.1) #Coverage 10%
    P = len(train_dataset[(train_dataset['class'] == 1)])
    N = len(train_dataset[(train_dataset['class'] == 0)])
    if positive_class == 0:
        P = len(train_dataset[(train_dataset['class'] == 0)])
        N = len(train_dataset[(train_dataset['class'] == 1)])

    q_func = rules_measures.get(q_measure, lambda: "Invalid Qualify Measure.")
    rule = rule_qfy_parameters[0]
    qfy_parameters = rule_qfy_parameters[1]
    p = qfy_parameters[0]
    n = qfy_parameters[1]
    if p > D:
        #Execute Qualify Function
        q = q_func(p, n, P, N)
        rule_dict = {
            "rule": rule,
            "q_value": q
        }
        return rule_dict
    return None

def get_qualified_rules(train, mw_rules, bw_rules, times, args, fold_no):
    global DIR_QFY
    step = file_content(DIR_QFY, fold_no, "log")
    step = step if len(step) else "rules_qualify"
    stopped_step = step_dict.get(step)

    step = "finished"
    if stopped_step == step_dict.get(step):
        mw_rules = pd.read_csv(os.path.join(DIR_QFY, str(fold_no) + "_mw_rules_qualify"))
        mw_rules.rule = mw_rules.rule.apply(ast.literal_eval)
        bw_rules = pd.read_csv(os.path.join(DIR_QFY, str(fold_no) + "_bw_rules_qualify"))
        bw_rules.rule = bw_rules.rule.apply(ast.literal_eval)
        time_l = file_content(DIR_QFY, fold_no, "times")
        return mw_rules, bw_rules, time_l

    time_l = times
    mw_qfy_rules = pd.DataFrame()
    bw_qfy_rules = pd.DataFrame()

    step = "rules_qualify"
    if stopped_step <= step_dict.get(step):
        update_log(DIR_QFY, fold_no, step)

        start = timeit.default_timer()
        mw_qfy_parameters = file_content(DIR_QFY, fold_no, "mw_qualify_parameters")
        if not len(mw_qfy_parameters) and mw_rules:
            logger.info("Getting Parameters for Qualifying MALWARES Rules.")
            qfy_parameters = parallelize_func(quality_parameters, mw_rules, const_parameters = [train, 1])
            save_to_file(qfy_parameters, DIR_QFY, fold_no, "mw_qualify_parameters")
        rules_qfy_parameters = list(zip(mw_rules, qfy_parameters))
        if rules_qfy_parameters:
            logger.info("Qualifying MALWARES Rules.")
            results = parallelize_func(quality_rules, rules_qfy_parameters, const_parameters = [train, args.qualify, 1])
            results = list(filter(None, results))
            mw_qfy_rules = pd.DataFrame(results)
            mw_qfy_rules = mw_qfy_rules.sort_values(by = ['q_value'], ascending = False)
            mw_qfy_rules.to_csv(os.path.join(DIR_QFY, str(fold_no) + "_mw_rules_qualify"), index = False)
        else:
            logger.info("No MALWARES Rules to Qualify.")

        bw_qfy_parameters = file_content(DIR_QFY, fold_no, "bw_qualify_parameters")
        if not len(bw_qfy_parameters) and bw_rules:
            logger.info("Getting Parameters for Qualifying BENIGNS Rules.")
            qfy_parameters = parallelize_func(quality_parameters, bw_rules, const_parameters = [train, 0])
            save_to_file(qfy_parameters, DIR_QFY, fold_no, "bw_qualify_parameters")
        rules_qfy_parameters = list(zip(bw_rules, qfy_parameters))

        if rules_qfy_parameters:
            logger.info("Qualifying BENIGNS Rules.")
            results = parallelize_func(quality_rules, rules_qfy_parameters, const_parameters = [train, args.qualify, 0])
            results = list(filter(None, results))
            bw_qfy_rules = pd.DataFrame(results)
            bw_qfy_rules = bw_qfy_rules.sort_values(by = ['q_value'], ascending = False)
            bw_qfy_rules.to_csv(os.path.join(DIR_QFY, str(fold_no) + "_bw_rules_qualify"), index = False)
        else:
            logger.info("No BENIGNS Rules to Qualify.")

        end = timeit.default_timer()
        time_tuple = (step, end - start)
        time_l.append(time_tuple)
        save_to_file(time_l, DIR_QFY, fold_no, "times")

    step = "finished"
    update_log(DIR_QFY, fold_no, step)
    return mw_qfy_rules, bw_qfy_rules, time_l

def test_apps(test, const_parameters):
    mw_rules = const_parameters[0]
    bw_rules = const_parameters[1]
    app_features = test[:-1]
    count_mw_rules = 0
    mw_qfy = 0.0
    bw_qfy = 0.0
    for r in mw_rules.itertuples():
        s = [app_features[i] for i in r.rule]
        if len(r.rule) == sum(s):
            count_mw_rules += 1
            q = r.q_value
            mw_qfy = q if q > mw_qfy else mw_qfy
    for r in bw_rules.itertuples():
        s = [app_features[i] for i in r.rule]
        if len(r.rule) == sum(s):
            q = r.q_value
            bw_qfy = q if q > bw_qfy else bw_qfy

    if bw_qfy > mw_qfy:
        count_mw_rules == 0

    p = count_mw_rules/len(mw_rules)
    return p

def get_results(test, mw_rules, bw_rules, times, args, fold_no):
    global DIR_TH
    step = file_content(DIR_TH, fold_no, "log")
    step = step if len(step) else "test_apps"
    stopped_step = step_dict.get(step)
    time_l = times
    step = "test_apps"
    pct_match_rules = []
    if stopped_step <= step_dict.get(step):
        if len(mw_rules) == 0:
            logger.warning("There Are No MALWARES Rules For Testing.")
            return None, None, None
        logger.info("{} MALWARES Rules To Be Tested.".format(len(mw_rules)))

        update_log(DIR_TH, fold_no, step)
        logger.info("Testing Applications.")

        start = timeit.default_timer()
        dataset_list  = test.values.tolist()
        pct_match_rules = parallelize_func(test_apps, dataset_list, const_parameters = [mw_rules, bw_rules, args])
        end = timeit.default_timer()
        time_tuple = (step, end - start)
        time_l.append(time_tuple)
        save_to_file(time_l, DIR_TH, fold_no, "times")
        save_to_file([pct_match_rules], DIR_TH, fold_no, step)

    step = "results_calc"
    result_dict ={}
    test_prediction = []
    if stopped_step == step_dict.get(step):
        pct_match_rules = file_content(DIR_TH, fold_no, "test_apps")
        time_l = file_content(DIR_TH, fold_no, "times")

    threshold = 0.0 if args.qualify else args.threshold
    class_ = test['class']
    i = 0
    for p in pct_match_rules:
        prediction = 1 if p > threshold else 0
        test_prediction.append(prediction)

    if stopped_step <= step_dict.get(step):
        update_log(DIR_TH, fold_no, step)
        test_classification = list(test['class'])
        result_dict = result_dataframe(test_classification, test_prediction, len(mw_rules))

    time_dict = dict(time_l)
    return result_dict, time_dict, test_prediction

def eqar(train, test, args, fold_no):
    mw_rules, bw_rules, time_l = get_rules(train, args, fold_no)
    if args.qualify:
        mw_rules, bw_rules, time_l = get_qualified_rules(train, mw_rules, bw_rules, time_l, args, fold_no)
        threshold = args.threshold if args.threshold else 0.2
        num_rules = int(len(mw_rules) * threshold)
        mw_rules = mw_rules[:num_rules]
        bw_rules = bw_rules[:num_rules]
    else:
        q_values = [0.0 for i in range(len(mw_rules))]
        d = {'rule': mw_rules, 'q_value': q_values}
        mw_rules = pd.DataFrame(d)
        q_values = [0.0 for i in range(len(bw_rules))]
        d = {'rule': bw_rules, 'q_value': q_values}
        bw_rules = pd.DataFrame(d)

    evaluation_metrics, runtime, prediction = get_results(test, mw_rules, bw_rules, time_l, args, fold_no)
    return evaluation_metrics, runtime, prediction

#if __name__=="__main__":
def run(dataset, dataset_file, args):
    global logger
    logger = logging.getLogger('EQAR')
    if args.verbose:
        logger.setLevel(logging.INFO)

    global DIR_BASE
    global DIR_QFY
    global DIR_TH
    DIR_BASE, DIR_QFY, DIR_TH = check_directories(dataset_file, args)

    dataset_class = dataset['class']

    skf = StratifiedKFold(n_splits = 5)
    fold_no = 1
    results_df = pd.DataFrame()
    times_list = []
    general_class = []
    general_prediction = []
    for train_index, test_index in skf.split(dataset, dataset_class):
        train = dataset.loc[train_index,:]
        test = dataset.loc[test_index,:]
        logger.info("Executing Fold {}".format(fold_no))

        if not args.verbose:
            spn = Spinner("Executing Fold {}".format(fold_no))
            spn.start()

        metrics_result, time_result, prediction_result = eqar(train, test, args, fold_no)

        if not args.verbose:
            spn.stop()

        if prediction_result:
            results_df = results_df.append(metrics_result, ignore_index = True)
            times_list.append(time_result)
            general_class += list(test['class'])
            general_prediction += prediction_result
        fold_no += 1

    results_df.to_csv(DIR_TH + "/model_results.csv", index = False)
    tdf = pd.DataFrame(times_list)
    tdf.to_csv(DIR_TH + "/time_results.csv", index = False)

    return general_class, general_prediction
