import sys
import os
import argparse
from termcolor import colored, cprint

cbar_models = []
ml_models = []
models_type =  ['cbar', 'ml']

def parse_args(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    list_group = parser.add_mutually_exclusive_group(required = False)
    list_group.add_argument(
        '--list-models', nargs = '+', metavar = 'MODEL_TYPE',
        help = "Show List of Models and Exit. Choices: " + str(models_type),
        choices = models_type, type = str)
    list_group.add_argument(
        '--list-models-all', help = 'Show List of All Models and Exit.',
        action = 'store_true')
    list_args =  any([x in ('--list-models', '--list-models-all') for x in argv])
    if list_args:
        args = parser.parse_args(argv)
        return args
    dataset_group = parser.add_mutually_exclusive_group(required = not list_args)
    dataset_group.add_argument(
        '-d', '--dataset', metavar = 'DATASET',
        help = 'Dataset (csv File).', type = str)
    dataset_group.add_argument(
        '--datasets', nargs = '+', metavar = 'DATASET',
        help = 'Datasets (csv Files).', type = str)
    dataset_group.add_argument(
        '--datasets-all', help = 'All Datasets (csv Files).',
        action = 'store_true')
    cbar_group = parser.add_mutually_exclusive_group(required = not list_args)
    cbar_group.add_argument(
        '--run-cbar', nargs = '+', metavar = 'CBAR',
        help = "Run Selected CBAR Models. Choices: " + str(cbar_models),
        choices = cbar_models, type = str)
    cbar_group.add_argument(
        '--run-cbar-all', help = "Run All CBAR Models.",
        action = 'store_true')
    ml_group = parser.add_mutually_exclusive_group(required = False)
    ml_group.add_argument(
        '--run-ml', nargs = '+', metavar = 'ML',
        help = "Run Selected Machine Learning (ML) Models. Choices: " + str(ml_models),
        choices = ml_models, type = str)
    ml_group.add_argument(
        '--run-ml-all', help = "Run All Machine Learning (ML) Models.",
        action = 'store_true')
    parser.add_argument(
        '--plot-graph-all', help = "Plot All Graphics.",
        action = 'store_true')

    cbar_complementar_args =  any([x in ('cba', 'cmar', 'eqar', '--run-cbar-all') for x in argv])
    group_cbar = parser.add_argument_group('Additional Parameters for CBA / CMAR / EQAR')
    if cbar_complementar_args:
        group_cbar.add_argument(
            '-s', '--min-support', metavar = 'float', required = False,
            help = 'Minimum Support (must be > 0.0 and < 1.0. Default: 0.1).',
            type = float, default = 0.1)
        group_cbar.add_argument(
            '-c', '--min-confidence', metavar = 'float', required = False,
            help = 'Minimum Confidence (must be > 0.0 and < 1.0. Default: 0.95).',
            type = float, default = 0.95)

    cbar_complementar_args =  any([x in ('cba', 'eqar', '--run-cbar-all') for x in argv])
    if cbar_complementar_args:
        group_cbar.add_argument(
            '-m', '--max-length', metavar = 'int', required = False,
            help = 'Max Length of Rules (Antecedent + Consequent). Default: 5.',
            type = int, default = 5)

    cbar_complementar_args =  any([x in ('eqar', '--run-cbar-all') for x in argv])
    group_eqar = parser.add_argument_group('Additional Parameters for EQAR')
    if cbar_complementar_args:
        group_eqar.add_argument(
            '-t', '--threshold', metavar = 'float',
            help = 'Percentage of Rules to be Used for Testing Samples. Default: 0.1.',
            type = float, default = 0.1)
        q_list = ['acc', 'c1', 'c2', 'bc', 'kap', 'corr', 'cov', 'prec']
        group_eqar.add_argument(
            '-q', '--qualify', metavar = 'QUALIFY', required = True,
            help = 'Metric for Rules Qualification. Choices: ' + str(q_list),
            choices = q_list, type = str)

    group_output = parser.add_argument_group('Parameters for Output')
    for m in cbar_models:
        output_args =  any([x in (m, '--run-cbar-all') for x in argv])
        if output_args:
            argument = '--output-cbar-' + m
            default_file = 'output_cbar_' + m + ".csv"
            help_txt = "Output to CBAR " + m.upper() + " Results. Default: " + default_file
            group_output.add_argument(
                argument, metavar = 'CSV_FILE',
                help = help_txt, type = str, default = default_file)
    for m in ml_models:
        output_args =  any([x in (m, '--run-ml-all') for x in argv])
        if output_args:
            argument = '--output-ml-' + m
            default_file = 'output_ml_' + m + ".csv"
            help_txt = "Output to ML " + m.upper() + " Results. Default: " + default_file
            group_output.add_argument(
                argument, metavar = 'CSV_FILE',
                help = help_txt, type = str, default = default_file)

    args = parser.parse_args(argv)
    return args

def list_models(models_to_list):
    for m in models_to_list:
        path_dir = os.path.join("./models", m)
        models_in_dir = get_dirs_list(path_dir)
        f = open(os.path.join(path_dir, "about.desc"), "r")
        model_desc = f.read()
        print(colored("\n>>> " + model_desc, 'green'))
        for i in models_in_dir:
            f = open(os.path.join(path_dir, i, "about.desc"), "r")
            model_desc = f.read()
            print(colored("\t" + model_desc, 'yellow'))
    exit(1)

def get_dirs_list(path):
    l = []
    for it in os.scandir(path):
        if it.is_dir():
            l.append(it.name)
    return l

if __name__=="__main__":
    cbar_models = get_dirs_list('./models/cbar')
    ml_models = get_dirs_list('./models/ml')

    args = parse_args(sys.argv[1:])
    print(args)

    if args.list_models:
        list_models(args.list_models)
    elif args.list_models_all:
        list_models(models_type)
