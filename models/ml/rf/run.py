import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
import sys
import os
from spinner import Spinner

#if __name__=="__main__":
def run(dataset_file, args):
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
        X_train = train.iloc[:,:-1] # features
        y_train = train.iloc[:,-1] # class
        test = dataset.loc[test_index,:]
        X_test = test.iloc[:,:-1] # features
        y_test = test.iloc[:,-1] # class
        clf = RandomForestClassifier(random_state = 0)
        spn = Spinner("Executing Fold {}".format(fold_no))
        spn.start()
        clf.fit(X_train, y_train)
        prediction_result = clf.predict(X_test)
        spn.stop()
        general_class += list(y_test)
        general_prediction += list(prediction_result)
        fold_no += 1

    return general_class, general_prediction
