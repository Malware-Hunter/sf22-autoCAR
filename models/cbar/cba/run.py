import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
from sklearn.model_selection import StratifiedKFold
import pandas as pd
import sys
import os
from spinner import Spinner

def exec_cba(path_to_r_file, train, test, s, c, l):
    r = ro.r
    r.source(path_to_r_file)
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_train = ro.conversion.py2rpy(train)
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_test = ro.conversion.py2rpy(test)

    p = r.cba(df_train, df_test, s, c, l)
    l = [x for x in p]
    return l

#if __name__=="__main__":
def run(dataset_file, args):
    path_to_r_file = os.path.dirname(os.path.realpath(__file__))
    path_to_r_file = os.path.join(path_to_r_file, "cba.r")
    try:
        dataset = pd.read_csv(dataset_file)
    except BaseException as e:
        print('Exception: {}'.format(e))
        exit(1)

    dataset_class = dataset['class']

    skf = StratifiedKFold(n_splits = 5)
    fold_no = 1
    general_class = []
    general_prediction = []
    for train_index, test_index in skf.split(dataset, dataset_class):
        train = dataset.loc[train_index,:]
        test = dataset.loc[test_index,:]
        spn = Spinner("Executing Fold {}".format(fold_no))
        spn.start()
        prediction_result = exec_cba(path_to_r_file, train, test, args.min_support, args.min_confidence, args.max_length)
        spn.stop()
        general_class += list(test['class'])
        general_prediction += prediction_result
        fold_no += 1

    return general_class, general_prediction







def function2(train, test):
    r = ro.r
    os.chdir('./')
    r.source(path, local = True)
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_train = ro.conversion.py2rpy(train)
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_test = ro.conversion.py2rpy(test)

    p = r.cba(df_train, df_test, 0.2, 0.95, 5)
    l = [x for x in p]
    return l
