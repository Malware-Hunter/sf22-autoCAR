import pandas as pd
from sklearn import svm
from sklearn.model_selection import StratifiedKFold
import sys
import os
from spinner import Spinner
from models.utils import *

#if __name__=="__main__":
def run(dataset, dataset_file, args):
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
        clf = svm.SVC()
        spn = Spinner("Executing Fold {}".format(fold_no))
        spn.start()
        clf.fit(X_train, y_train)
        prediction_result = clf.predict(X_test)
        spn.stop()
        general_class += list(y_test)
        general_prediction += list(prediction_result)
        fold_no += 1

    return general_class, general_prediction
