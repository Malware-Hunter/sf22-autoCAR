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
from models.utils import *

#-----------------------------------------------------------------------

DIR_BASE = ""
DIR_QFY = ""
DIR_TH = ""

def execute_fim(parameters):
    p = parameters[0,:]
    algorithm = p[1].algorithm
    support = p[3] * 100
    confidence = p[4] * 100
    max_l = p[1].max_length
    report = 'scl'
    print("Running FIM: Generating", p[2], "Association Rules.",
            "Sup >> {:.2f}".format(support),
            "Conf >> {:.2f}".format(confidence))
    algorithm_fim = globals()[algorithm]
    result = algorithm_fim(p[0], target='r', zmin=2, zmax=max_l, supp=support,
                    conf=confidence, report=report, mode='o')
    r = to_pandas_dataframe(result, report)
    r = generate_unique_rules(r, p[1].min_lift, p[2])

    pct = (1.0 - (len(r)/len(result))) * 100.0 if len(result) != 0 else 0.0
    print("Generate {}".format(len(r)), p[2], "Association Rules ({:.3f})".format(pct))
    return r

#def rules_subset(list_a, list_b, max_l):
def rules_subset(list_a, const_parameter):
    list_b = const_parameter[0]
    max_l = const_parameter[1]
    l = []
    for i in range(2, max_l):
        print("[SUBSET] Processing Rules of Length", i)
        rules_to_check = [r for r in list_a if len(r) == i]
        majors_rules = [r for r in list_b if len(r) > i]
        for rule in tqdm(rules_to_check):
            #li = [r for r in lb if rule[0] <= r[0] and rule[-1] >= r[-1]]
            is_subset = any(set(rule).issubset(r) for r in majors_rules)
            if not is_subset:
                l.append(rule)
    la = [r for r in list_a if len(r) == max_l]
    l += la
    return l

#def rules_superset(list_a, max_l):
def rules_superset(list_a, const_parameter):
    list_b = const_parameter[0]
    max_l = const_parameter[1]
    l = []
    for i in range(3, max_l + 1):
        print("[SUPERSET] Processing Rules of Length", i)
        rules_to_check = [r for r in list_a if len(r) == i]
        minors_rules = [r for r in list_b if len(r) < i]
        for rule in tqdm(rules_to_check):
            #li = [r for r in minors_rules if rule[0] <= r[0] and rule[-1] >= r[-1]]
            is_superset = any(set(rule).issuperset(r) for r in minors_rules)
            if not is_superset:
                l.append(rule)
    la = [r for r in list_a if len(r) == 2]
    l += la
    return l

def test_apps(test, const_parameter):
    mw_rules = const_parameter[0]
    mw_max_q_value = max(list(mw_rules['q_value']))
    bw_rules = const_parameter[1]
    bw_max_q_value = max(list(bw_rules['q_value']))
    args = const_parameter[2]

    features_test = test.drop(['class'], axis=1)
    pct_match_rules = []

    for i in tqdm(range(0, len(test))):
        count_mw_rules = 0
        app_ft = features_test.values[i,:]
        mw_qfy = 0.0
        bw_qfy = 0.0
        for r in mw_rules.itertuples():
            if len(r.rule) == app_ft[list(r.rule)].sum():
                count_mw_rules += 1
                q = r.q_value
                mw_qfy = q if q > mw_qfy else mw_qfy

        for r in bw_rules.itertuples():
            if len(r.rule) == app_ft[list(r.rule)].sum():
                q = r.q_value
                bw_qfy = q if q > bw_qfy else bw_qfy

        if bw_qfy > mw_qfy:
            count_mw_rules == 0

        p = count_mw_rules/len(mw_rules)
        pct_match_rules.append(p)
    return pct_match_rules

def quality_parameters(rules, const_parameter):
    dataset = const_parameter[0]
    classification = const_parameter[1]
    rules_metrics = []
    features = dataset.drop(['class'], axis=1)
    class_ = list(dataset['class'])
    for r in tqdm(rules):
        rule_coverage = 0 # == p + n
        p = 0
        for i in range(0, len(dataset)):
            app_ft = features.values[i,:]
            if len(r) == app_ft[list(r)].sum():
                rule_coverage += 1
                if class_[i] == classification:
                    p += 1
        n = rule_coverage - p
        rules_metrics.append([p, n])
    return rules_metrics

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

        spn = Spinner('Preparing MALWARES Data')
        spn.start()
        mw_fim = to_fim_format(mw_dataset)
        spn.stop()

        spn = Spinner('Preparing BENIGNS Data')
        spn.start()
        bw_fim = to_fim_format(bw_dataset)
        spn.stop()

        mw_sup = args.min_support
        bw_sup = args.min_support
        mw_conf = args.min_confidence
        bw_conf = args.min_confidence

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
        print("Generating Unique Rules: INTERSECTION.")
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
        print("Generating Unique Rules: SUPERSET.")
        start = timeit.default_timer()
        mw_rules = list(mw_rules)
        bw_rules = list(bw_rules)
        p = np.array(mw_rules, dtype=object)
        mw_result = parallelize_func(rules_superset, p, const_parameter = [mw_rules, args.max_length])
        p = np.array(bw_rules, dtype=object)
        bw_result = parallelize_func(rules_superset, p, const_parameter = [bw_rules, args.max_length])
        end = timeit.default_timer()
        time_tuple = (step, end - start)
        time_l.append(time_tuple)
        mw_rules = [l for r in mw_result for l in r]
        bw_rules = [l for r in bw_result for l in r]
        save_data(mw_rules, bw_rules, time_l, DIR_BASE, fold_no)

    step = "rules_subset"
    if stopped_step == step_dict.get(step):
        mw_rules, bw_rules, time_l = load_data(DIR_BASE, fold_no, stopped_step)

    if stopped_step <= step_dict.get(step):
        update_log(DIR_BASE, fold_no, step)
        print("Generating Unique Rules: SUBSET.")
        start = timeit.default_timer()
        mw_rules = list(mw_rules)
        bw_rules = list(bw_rules)
        p = np.array(mw_rules, dtype=object)
        mw_result = parallelize_func(rules_subset, p, const_parameter = [bw_rules, args.max_length])
        p = np.array(bw_rules, dtype=object)
        bw_result = parallelize_func(rules_subset, p, const_parameter = [mw_rules, args.max_length])
        end = timeit.default_timer()
        time_tuple = (step, end - start)
        time_l.append(time_tuple)
        mw_rules = [l for r in mw_result for l in r]
        bw_rules = [l for r in bw_result for l in r]
        save_data(mw_rules, bw_rules, time_l, DIR_BASE, fold_no)

    step = "finished"
    update_log(DIR_BASE, fold_no, step)
    return mw_rules, bw_rules, time_l

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
            print(colored("There Are No MALWARES Rules For Testing",'red'))
            return None, None, None
        print(colored("{} MALWARES Rules To Be Tested.".format(len(mw_rules)), 'green'))

        update_log(DIR_TH, fold_no, step)
        print("Testing Applications.")
        start = timeit.default_timer()
        result = parallelize_func(test_apps, test, const_parameter = [mw_rules, bw_rules, args])
        end = timeit.default_timer()
        time_tuple = (step, end - start)
        time_l.append(time_tuple)
        save_to_file(time_l, DIR_TH, fold_no, "times")
        pct_match_rules  = [l for r in result for l in r]
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

#def quality_rules(rules, dataset, q_measure):
def quality_rules(rules, const_parameter):
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
    dataset = const_parameter[0]
    q_measure = const_parameter[1]
    positive_class = const_parameter[2]
    D = int(len(dataset) * 0.1) #Coverage 10%
    P = len(dataset[(dataset['class'] == 1)])
    N = len(dataset[(dataset['class'] == 0)])
    if positive_class == 0:
        P = len(dataset[(dataset['class'] == 0)])
        N = len(dataset[(dataset['class'] == 1)])
    rules_metrics = []
    func = rules_measures.get(q_measure, lambda: "Invalid Qualify Measure")
    for index, row in rules.iterrows():
        r = row['rule']
        p = row['qualify_parameters'][0]
        n = row['qualify_parameters'][1]
        if p > D:
            #execute the function
            q = func(p, n, P, N)
            #print(q)
            rule_dict = {
                "rule": r,
                "q_value": q
            }
            rules_metrics.append(rule_dict)
    rdf = pd.DataFrame(rules_metrics)
    return rdf

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
    mw_qfy_rules = []
    bw_qfy_rules = []

    step = "rules_qualify"
    if stopped_step <= step_dict.get(step):
        update_log(DIR_QFY, fold_no, step)
        start = timeit.default_timer()
        print("Qualifying MALWARES Rules.")
        mw_qfy_parameters = file_content(DIR_QFY, fold_no, "mw_qualify_parameters")
        if not len(mw_qfy_parameters):
            p = np.array(mw_rules, dtype=object)
            results = parallelize_func(quality_parameters, p, const_parameter = [train, 1])
            result  = [l for r in results for l in r]
            save_to_file(result, DIR_QFY, fold_no, "mw_qualify_parameters")
        mw_df = pd.DataFrame(list(zip(mw_rules, result)), columns =['rule', 'qualify_parameters'])
        results = parallelize_func(quality_rules, mw_df, const_parameter = [train, args.qualify, 1])
        mw_qfy_rules = pd.concat(results)
        mw_qfy_rules = mw_qfy_rules.sort_values(by=['q_value'], ascending=False)

        print("Qualifying BENIGNS Rules.")
        bw_qfy_parameters = file_content(DIR_QFY, fold_no, "bw_qualify_parameters")
        if not len(bw_qfy_parameters):
            p = np.array(bw_rules, dtype=object)
            results = parallelize_func(quality_parameters, p, const_parameter = [train, 0])
            result  = [l for r in results for l in r]
            save_to_file(result, DIR_QFY, fold_no, "bw_qualify_parameters")
        bw_df = pd.DataFrame(list(zip(bw_rules, result)), columns =['rule', 'qualify_parameters'])
        results = parallelize_func(quality_rules, bw_df, const_parameter = [train, args.qualify, 0])
        bw_qfy_rules = pd.concat(results)
        bw_qfy_rules = bw_qfy_rules.sort_values(by=['q_value'], ascending=False)

        end = timeit.default_timer()
        time_tuple = (step, end - start)
        time_l.append(time_tuple)
        save_to_file(time_l, DIR_QFY, fold_no, "times")
        mw_qfy_rules.to_csv(os.path.join(DIR_QFY, str(fold_no) + "_mw_rules_qualify"), index = False)
        bw_qfy_rules.to_csv(os.path.join(DIR_QFY, str(fold_no) + "_bw_rules_qualify"), index = False)

    step = "finished"
    update_log(DIR_QFY, fold_no, step)
    return mw_qfy_rules, bw_qfy_rules, time_l

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
def run(dataset_file, args):
    try:
        dataset = pd.read_csv(dataset_file)
    except BaseException as e:
        print('Exception: {}'.format(e))
        exit(1)
    global DIR_BASE
    global DIR_QFY
    global DIR_TH
    DIR_BASE, DIR_QFY, DIR_TH = check_directories(args)

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
        print("Executing Fold {}".format(fold_no))
        metrics_result, time_result, prediction_result = eqar(train, test, args, fold_no)
        results_df = results_df.append(metrics_result, ignore_index = True)
        times_list.append(time_result)
        general_class += list(test['class'])
        general_prediction += prediction_result
        fold_no += 1

    results_df.to_csv(DIR_TH + "/model_results.csv", index = False)
    tdf = pd.DataFrame(times_list)
    tdf.to_csv(DIR_TH + "/time_results.csv", index = False)

    return general_class, general_prediction
