import numpy as np
import pandas as pd
import csv
from tqdm import tqdm
from multiprocessing import cpu_count, Pool
from functools import partial
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from termcolor import colored, cprint
import shutil
import os

def parallelize_func(func, parameters, const_parameter = None, cores = cpu_count()):
    parameters_split = np.array_split(parameters, cores)
    pool = Pool(cores)
    result = []
    if const_parameter == None:
        result.append(pool.map(func, parameters_split))
    else:
        result.append(pool.map(partial(func, const_parameter = const_parameter), parameters_split))
    pool.close()
    pool.join()
    return result[0]

def file_content(dir_path, fold_no, file):
    f_name = os.path.join(dir_path, str(fold_no) + "_" + file)
    ct = []
    try:
        with open(f_name) as f:
            if file == "log":
                ct = [l for l in f]
                ct = ct[0]
            elif file in ["mw_rules", "bw_rules", "mw_qualify_parameters", "bw_qualify_parameters"]:
                ct = [list(map(int, l.split(','))) for l in f]
            elif file in ["rules_intersection", "rules_subset", "rules_superset", "rules_qualify"]:# or file.startswith("rules_qualify"):
                ct = [tuple(map(int, l.split(','))) for l in f]
            elif file == "test_apps":
                ct = [list(map(float, l.split(','))) for l in f]
                ct = ct[0]
            elif file == "times":
                ct = [(l.split(',')[0], float(l.split(',')[1])) for l in f]
        return ct
    except BaseException as e:
        #print(e)
        return ct

def update_log(dir_path, fold_no, step):
    f_name = os.path.join(dir_path, str(fold_no) + "_log")
    with open(f_name, 'w') as f:
        f.write(step)

def save_to_file(obj_list, dir_path, fold_no, step):
    f_name = os.path.join(dir_path, str(fold_no) + "_" + step)
    with open(f_name,"w", newline='') as f:
        f_writer = csv.writer(f)
        for obj in obj_list:
            f_writer.writerow(obj)

def load_data(location, fold_no, stopped_step):
    mw_rules = file_content(location, fold_no, "mw_rules")
    bw_rules = file_content(location, fold_no, "bw_rules")
    time_l = file_content(location, fold_no, "times")
    time_l = time_l[:stopped_step + 1]
    return mw_rules, bw_rules, time_l

def save_data(mw_rules, bw_rules, time_l, location, fold_no):
    save_to_file(mw_rules, location, fold_no, "mw_rules")
    save_to_file(bw_rules, location, fold_no, "bw_rules")
    save_to_file(time_l, location, fold_no, "times")

def check_directories(args):

    # - ->> directories to save data <<- -#
    root_path = os.path.dirname(os.path.realpath(__file__))
    dir_name = (args.dataset).split('/')[-1]
    dir_name = dir_name.split('.')[0]
    dir_name += "_S" + str(int(args.min_support * 100.0))
    dir_name += "_C" + str(int(args.min_confidence * 100.0))

    path = os.path.join(root_path, "run_files", dir_name)
    DIR_BASE = path
    if args.overwrite and os.path.exists(path):
        shutil.rmtree(path)

    if args.qualify:
        path = os.path.join(path, args.qualify)
        DIR_QFY = path

    th_int = int(args.threshold * 100.0)
    th_str = "0" + str(th_int) if th_int < 10 else str(th_int)
    th_dir = "T" + th_str

    DIR_TH = os.path.join(path, th_dir)
    if not os.path.exists(DIR_TH):
        os.makedirs(DIR_TH)

    return DIR_BASE, DIR_QFY, DIR_TH

def dataset_transaction(dataset):
    num_rows = dataset.shape[0]
    num_cols = dataset.shape[1]
    t = []
    for i in tqdm(range(0,num_rows)):
        l = []
        for j in range(0,num_cols):
            if dataset.values[i][j] != 0:
                l.append(j)
        t.append(l)
    return t

#Dictionary For Column Names
report_colnames = {
    'a': 'support_itemset_absolute',
    's': 'support_itemset_relative',
    'S': 'support_itemset_relative_pct',
    'b': 'support_antecedent_absolute',
    'x': 'support_antecedent_relative',
    'X': 'support_antecedent_relative_pct',
    'h': 'support_consequent_absolute',
    'y': 'support_consequent_relative',
    'Y': 'support_consequent_relative_pct',
    'c': 'confidence',
    'C': 'confidence_pct',
    'l': 'lift',
    'L': 'lift_pct',
    'e': 'evaluation',
    'E': 'evaluation_pct',
    'Q': 'xx',
    'S': 'support_emptyset',
}

def to_fim_format(dataset):
    result = parallelize_func(dataset_transaction, dataset)
    data = []
    for i in range(0, len(result)):
        for j in range(0, len(result[i])):
            data.append(result[i][j])
    return data

def to_pandas_dataframe(data, report):
    colnames = ['consequent', 'antecedent'] + [report_colnames.get(r, r) for r in list(report)]
    df = pd.DataFrame(data, columns=colnames)
    s = df[['consequent', 'antecedent']].values.tolist()
    size_list = [len({i[0]} | set(i[1])) for i in s]
    df['size'] = size_list
    df = df.sort_values(['support_itemset_relative','confidence', 'size'], ascending = [False, False, True])
    r_count = int(len(df) * 0.5)
    return df.head(r_count)

def generate_unique_rules(dataset_df, lift, dataset_type):
    rules = []
    if not dataset_df.empty:
        r = dataset_df[(dataset_df['lift'] >= lift)]
        print("Deleting", dataset_type, "Repeated Rules")
        s = r[['consequent', 'antecedent']].values.tolist()
        r_list = [sorted({i[0]} | set(i[1])) for i in s]
        rules = list(map(list, set(map(lambda i: tuple(i), r_list))))
    return rules
