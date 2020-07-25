'''
Created on Jun 23, 2017

@author: Michael Pradel

Last Changed on July 25, 2020

@by: Sabine Zach
'''

import sys
import json
from os.path import join
from os import getcwd
from collections import Counter, namedtuple
import math
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Dropout
import random
import time
import numpy as np
import Util
import LearningDataSwappedArgs
import LearningDataBinOperator
import LearningDataSwappedBinOperands
import LearningDataIncorrectBinaryOperand
##not yet implemented
##import LearningDataIncorrectAssignment
##import LearningDataMissingArg

##not used
##name_embedding_size = 200
##file_name_embedding_size = 50
##type_embedding_size = 5

Anomaly = namedtuple("Anomaly", ["message", "score"])

def parse_data_paths(args):
    new_data_paths = []
    mode = None
    for arg in args:
        if arg == "--newData":
            assert mode == None
            mode = "newData"
        else:
            path = join(getcwd(), arg)
            if mode == "newData":
                new_data_paths.append(path)
            else:
                print("Incorrect arguments")
                sys.exit(0)
    return new_data_paths

def prepare_xy_pairs(data_paths, learning_data):
    xs = []
    ys = []
    code_pieces = [] # keep calls in addition to encoding as x,y pairs (to report detected anomalies)
    
    for code_piece in Util.DataReader(data_paths):
        learning_data.code_to_xy_pairs(code_piece, xs, ys, name_to_vector, type_to_vector, node_type_to_vector, code_pieces)
    x_length = len(xs[0])
    
    print("Stats: " + str(learning_data.stats))
    print("Number of x,y pairs: " + str(len(xs)))
    print("Length of x vectors: " + str(x_length))
    xs = np.array(xs)
    ys = np.array(ys)
    return [xs, ys, code_pieces]

def sample_xy_pairs(xs, ys, number_buggy):
    sampled_xs = []
    sampled_ys = []
    buggy_indices = []
    for i, y in enumerate(ys):
        if y == [1]:
            buggy_indices.append(i)
    sampled_buggy_indices = set(np.random.choice(buggy_indices, size=number_buggy, replace=False))
    for i, x in enumerate(xs):
        y = ys[i]
        if y == [0] or i in sampled_buggy_indices:
            sampled_xs.append(x)
            sampled_ys.append(y)
    return sampled_xs, sampled_ys

if __name__ == '__main__':
    # arguments (for learning new model): what <p_threshold> --load <model file> <name to vector file> <type to vector file> <AST node type to vector file> --newData <list of data files in json format>
    #  what is one of: SwappedArgs,
    #                  BinOperator,
    #                  SwappedBinOperands,
    #                  IncorrectBinaryOperand,
    #                  IncorrectAssignment
    #                  MissingArg
    #
    # not yet implemented bug patterns are the following:
    #
    # "IncorrectAssignment"
    # "MissingArg"
    #

    print("BugFind started with " + str(sys.argv))

    what = sys.argv[1]
    p_threshold = float(sys.argv[2])
    option = sys.argv[3]
    if option == "--load":
        model_file = sys.argv[4]
        name_to_vector_file = join(getcwd(), sys.argv[5])
        type_to_vector_file = join(getcwd(), sys.argv[6])
        node_type_to_vector_file = join(getcwd(), sys.argv[7])
        new_data_paths = parse_data_paths(sys.argv[8:])
    else:
        print("Incorrect arguments")
        sys.exit(1)
    
    with open(name_to_vector_file) as f:
        name_to_vector = json.load(f)
    with open(type_to_vector_file) as f:
        type_to_vector = json.load(f)
    with open(node_type_to_vector_file) as f:
        node_type_to_vector = json.load(f)
    
    #-------------------------------------Find------------------------------------------
    time_start = time.time()

    if what == "SwappedArgs":
        learning_data = LearningDataSwappedArgs.LearningData()
    elif what == "BinOperator":
        learning_data = LearningDataBinOperator.LearningData()
    elif what == "SwappedBinOperands":
        learning_data = LearningDataSwappedBinOperands.LearningData()
    elif what == "IncorrectBinaryOperand":
        learning_data = LearningDataIncorrectBinaryOperand.LearningData()
    ##not yet used
    ##elif what == "IncorrectAssignment":
    ##    learning_data = LearningDataIncorrectAssignment.LearningData()
    ##elif what == "MissingArg":
    ##    learning_data = LearningDataMissingArg.LearningData()
    else:
        print("Incorrect argument for 'what'")
        sys.exit(1)
    
    print("Statistics on new data:")
    learning_data.pre_scan(new_data_paths)
    learning_data.resetStats()
    
    # prepare x,y pairs
    print("Preparing xy pairs for new data:")
    xs_newdata, ys_dummy, code_pieces_prediction = prepare_xy_pairs(new_data_paths, learning_data)
    x_length = len(xs_newdata[0])

    print("New Data examples   : " + str(len(xs_newdata)))
    print(learning_data.stats)
    
    # use already generated model (see DeepBugs - Part I - LearnBugs)
    model = load_model(model_file)
    print("Loaded model.")

    ##predict ys for every selected piece of code
    ys_prediction = model.predict(xs_newdata)

    time_done = time.time()
    print("Time for prediction (seconds): " + str(round(time_done - time_start)))

    ##------------------------------------------------
    # produce prediction message
    predictions = []

    for idx in range(0, len(xs_newdata)):
        p = ys_prediction[idx][0]    # probab, expect 0, when code is correct
        c = code_pieces_prediction[idx]
        message = "Prediction : " + str(p) + " | " + what + " | " + c.to_message() + "\n\n"

        #only pick codepieces with prediction > p
        if p > p_threshold:
            predictions.append(message)

    if predictions == []:
        no_examples = "No data examples found in input data with prediction > " + str(p_threshold)
        predictions.append(no_examples)

    # log the messages to file
    f_inspect = open('predictions.txt', 'w+')
    for message in predictions:
        f_inspect.write(message + "\n")
    print("predictions written to file : predictions.txt")
    f_inspect.close()

    # print the messages
    print("Predictions:\n")
    print("------------\n")
    for message in predictions:
        print(message + "\n")
    print("------------\n")
    print("Predictions finished")
    ##------------------------------------------------

    #-------------------------------------Find------------------------------------------
