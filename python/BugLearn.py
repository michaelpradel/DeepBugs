'''
Created on Jun 23, 2017

@author: Michael Pradel

Last Changed on Apr 28, 2020

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
import LearningDataIncorrectAssignment
import LearningDataMissingArg

name_embedding_size = 200
file_name_embedding_size = 50
type_embedding_size = 5

Anomaly = namedtuple("Anomaly", ["message", "score"])

def parse_data_paths(args):
    training_data_paths = []
    eval_data_paths = []
    mode = None
    for arg in args:
        if arg == "--trainingData":
            assert mode == None
            mode = "trainingData"
        elif arg == "--validationData":
            assert mode == "trainingData"
            mode = "validationData"
        else:
            path = join(getcwd(), arg)
            if mode == "trainingData":
                training_data_paths.append(path)
            elif mode == "validationData":
                eval_data_paths.append(path)
            else:
                print("Incorrect arguments")
                sys.exit(0)
    return [training_data_paths, eval_data_paths]

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
    # arguments (for learning new model): what --learn <name to vector file> <type to vector file> <AST node type to vector file> --trainingData <list of call data files> --validationData <list of call data files>
    #   what is one of: SwappedArgs, BinOperator, SwappedBinOperands, IncorrectBinaryOperand, IncorrectAssignment
    print("BugLearn started with " + str(sys.argv))
    time_start = time.time()
    what = sys.argv[1]
    option = sys.argv[2]
    if option == "--learn":
        name_to_vector_file = join(getcwd(), sys.argv[3])
        type_to_vector_file = join(getcwd(), sys.argv[4])
        node_type_to_vector_file = join(getcwd(), sys.argv[5])
        training_data_paths, validation_data_paths = parse_data_paths(sys.argv[6:])
    else:
        print("Incorrect arguments")
        sys.exit(1)
    
    with open(name_to_vector_file) as f:
        name_to_vector = json.load(f)
    with open(type_to_vector_file) as f:
        type_to_vector = json.load(f)
    with open(node_type_to_vector_file) as f:
        node_type_to_vector = json.load(f)
    
    if what == "SwappedArgs":
        learning_data = LearningDataSwappedArgs.LearningData()
    elif what == "BinOperator":
        learning_data = LearningDataBinOperator.LearningData()
    elif what == "SwappedBinOperands":
        learning_data = LearningDataSwappedBinOperands.LearningData()
    elif what == "IncorrectBinaryOperand":
        learning_data = LearningDataIncorrectBinaryOperand.LearningData()
    elif what == "IncorrectAssignment":
        learning_data = LearningDataIncorrectAssignment.LearningData()
    elif what == "MissingArg":
        learning_data = LearningDataMissingArg.LearningData()
    else:
        print("Incorrect argument for 'what'")
        sys.exit(1)
    
    print("Statistics on training data:")
    learning_data.pre_scan(training_data_paths, validation_data_paths)
    
    # prepare x,y pairs for learning
    print("Preparing xy pairs for training data:")
    learning_data.resetStats()
    xs_training, ys_training, _ = prepare_xy_pairs(training_data_paths, learning_data)
    x_length = len(xs_training[0])
    print("Training examples   : " + str(len(xs_training)))
    print(learning_data.stats)
    
    # create a model (simple feedforward network)
    model = Sequential()
    model.add(Dropout(0.2, input_shape=(x_length,)))
    model.add(Dense(200, input_dim=x_length, activation="relu", kernel_initializer='normal'))
    model.add(Dropout(0.2))
    #model.add(Dense(200, activation="relu"))
    model.add(Dense(1, activation="sigmoid", kernel_initializer='normal'))
     
    # train model
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    history = model.fit(xs_training, ys_training, batch_size=100, epochs=10, verbose=1)
        
    time_stamp = math.floor(time.time() * 1000)
    model.save("bug_detection_model_"+str(time_stamp))
    
    time_learning_done = time.time()
    print("Time for learning (seconds): " + str(round(time_learning_done - time_start)))

    print("------------\n")
    print("Bug Detection Model saved")
