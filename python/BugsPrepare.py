'''
Created on Mar 17, 2020

@author: Sabine Zach

Last Changed on Apr 24, 2020

@by: Sabine Zach
'''

import numpy as np
import Util

from os import getcwd
from os.path import join

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

def prepare_xy_pairs(learn_on, name_to_vector, type_to_vector, node_type_to_vector, data_paths, learning_data):
    xs = []
    ys = []
    code_pieces = [] # keep calls in addition to encoding as x,y pairs (to report detected anomalies)

    for code_piece in Util.DataReader(data_paths):
        learning_data.code_to_xy_pairs(learn_on, code_piece, xs, ys, name_to_vector, type_to_vector, node_type_to_vector, code_pieces)
    x_length = len(xs[0])

    print("Stats: " + str(learning_data.stats))
    print("Number of x,y pairs: " + str(len(xs)))
    print("Length of x vectors: " + str(x_length))
    xs = np.array(xs)
    ys = np.array(ys)
    return [xs, ys, code_pieces]
