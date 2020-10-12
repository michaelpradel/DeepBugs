'''
Created on Jun 23, 2017

@author: Michael Pradel, Sabine Zach
'''

import sys
import json
from os.path import join
from os import getcwd
from collections import namedtuple
from tensorflow.python.keras.models import load_model
import time
import numpy as np
import Util
import LearningDataSwappedArgs
import LearningDataBinOperator
import LearningDataSwappedBinOperands
import LearningDataIncorrectBinaryOperand
import LearningDataIncorrectAssignment
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    "--pattern", help="Kind of data to extract", choices=["SwappedArgs", "BinOperator", "SwappedBinOperands", "IncorrectBinaryOperand", "IncorrectAssignment"], required=True)
parser.add_argument(
    "--token_emb", help="JSON file with token embeddings", required=True)
parser.add_argument(
    "--type_emb", help="JSON file with type embeddings", required=True)
parser.add_argument(
    "--node_emb", help="JSON file with AST node embeddings", required=True)
parser.add_argument(
    "--testing_data", help="JSON files with testing data", required=True, nargs="+")
parser.add_argument(
    "--model", help="Directory with trained model", required=True)
parser.add_argument(
    "--threshold", help="Threshold for reporting warnings (0.0 reports most, 1.0 reports fewest)", required=True)


Anomaly = namedtuple("Anomaly", ["message", "score"])


def prepare_xy_pairs(gen_negatives, data_paths, learning_data):
    xs = []
    ys = []
    # keep calls in addition to encoding as x,y pairs (to report detected anomalies)
    code_pieces = []

    for code_piece in Util.DataReader(data_paths):
        learning_data.code_to_xy_pairs(gen_negatives, code_piece, xs, ys,
                                       name_to_vector, type_to_vector, node_type_to_vector, code_pieces)
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
    sampled_buggy_indices = set(np.random.choice(
        buggy_indices, size=number_buggy, replace=False))
    for i, x in enumerate(xs):
        y = ys[i]
        if y == [0] or i in sampled_buggy_indices:
            sampled_xs.append(x)
            sampled_ys.append(y)
    return sampled_xs, sampled_ys


if __name__ == '__main__':
    print("BugFind started with " + str(sys.argv))

    args = parser.parse_args()
    pattern = args.pattern
    name_to_vector_file = args.token_emb
    type_to_vector_file = args.type_emb
    node_type_to_vector_file = args.node_emb
    new_data_paths = args.testing_data
    p_threshold = float(args.threshold)
    model_dir = args.model

    with open(name_to_vector_file) as f:
        name_to_vector = json.load(f)
    with open(type_to_vector_file) as f:
        type_to_vector = json.load(f)
    with open(node_type_to_vector_file) as f:
        node_type_to_vector = json.load(f)

    # -------------------------------------Find------------------------------------------
    time_start = time.time()

    if pattern == "SwappedArgs":
        learning_data = LearningDataSwappedArgs.LearningData()
    elif pattern == "BinOperator":
        learning_data = LearningDataBinOperator.LearningData()
    elif pattern == "SwappedBinOperands":
        learning_data = LearningDataSwappedBinOperands.LearningData()
    elif pattern == "IncorrectBinaryOperand":
        learning_data = LearningDataIncorrectBinaryOperand.LearningData()
    elif pattern == "IncorrectAssignment":
        learning_data = LearningDataIncorrectAssignment.LearningData()
    else:
        raise Exception(f"Unexpected bug pattern: {pattern}")
    # not yet used
    # elif what == "MissingArg":
    ##    learning_data = LearningDataMissingArg.LearningData()

    print("Statistics on new data:")
    learning_data.pre_scan(new_data_paths)
    learning_data.resetStats()

    # prepare x,y pairs
    print("Preparing xy pairs for new data:")
    xs_newdata, ys_dummy, code_pieces_prediction = prepare_xy_pairs(
        False, new_data_paths, learning_data)
    x_length = len(xs_newdata[0])

    print("New Data examples   : " + str(len(xs_newdata)))
    print(learning_data.stats)

    model = load_model(model_dir)
    print("Loaded model.")

    # predict ys for every selected piece of code
    ys_prediction = model.predict(xs_newdata)

    time_done = time.time()
    print("Time for prediction (seconds): " +
          str(round(time_done - time_start)))

    # produce prediction message
    predictions = []

    for idx in range(0, len(xs_newdata)):
        p = ys_prediction[idx][0]    # probab, expect 0, when code is correct
        c = code_pieces_prediction[idx]
        message = "Prediction : " + \
            str(p) + " | " + pattern + " | " + c.to_message()

        # only pick codepieces with prediction > p
        if p > p_threshold:
            predictions.append(message)

    if predictions == []:
        no_examples = "No data examples found in input data with prediction > " + \
            str(p_threshold)
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
