'''
Created on Nov 13, 2017

@author: Michael Pradel
'''

import Util
from collections import Counter
import random

type_embedding_size = 5
node_type_embedding_size = 8 # if changing here, then also change in LearningDataBinOperator

commutative_operators = ["+", "==", "===", "!==", "!=", "*", "|", "&", "^"]

class CodePiece(object):
    def __init__(self, left, right, op, src):
        self.left = left
        self.right = right
        self.op = op
        self.src = src
    
    def to_message(self):
        return str(self.src) + " | " + str(self.left) + " | " + str(self.op) + " | " + str(self.right)
    
class LearningData(object):
    def __init__(self):
        self.all_operators = None
        self.stats = {}

    def pre_scan(self, training_data_paths, validation_data_paths):
        all_operators_set = set()
        for bin_op in Util.DataReader(training_data_paths):
            all_operators_set.add(bin_op["op"])
        for bin_op in Util.DataReader(validation_data_paths):
            all_operators_set.add(bin_op["op"])
        self.all_operators = list(all_operators_set)
    
    def code_to_xy_pairs(self, bin_op, xs, ys, name_to_vector, type_to_vector, node_type_to_vector, code_pieces):
        left = bin_op["left"]
        right = bin_op["right"]
        operator = bin_op["op"]
        left_type = bin_op["leftType"]
        right_type = bin_op["rightType"]
        parent = bin_op["parent"]
        grand_parent = bin_op["grandParent"]
        src = bin_op["src"]
        if not (left in name_to_vector):
            return
        if not (right in name_to_vector):
            return
        if operator in commutative_operators:
            return
        
        left_vector = name_to_vector[left]
        right_vector = name_to_vector[right]
        operator_vector = [0] * len(self.all_operators)
        operator_vector[self.all_operators.index(operator)] = 1
        left_type_vector = type_to_vector.get(left_type, [0]*type_embedding_size)
        right_type_vector = type_to_vector.get(right_type, [0]*type_embedding_size)
        parent_vector = node_type_to_vector[parent]
        grand_parent_vector = node_type_to_vector[grand_parent]
        
        # for all xy-pairs: y value = probability that incorrect
        x_correct = left_vector + right_vector + operator_vector + left_type_vector + right_type_vector + parent_vector + grand_parent_vector
        y_correct = [0]
        xs.append(x_correct)
        ys.append(y_correct)
        code_pieces.append(CodePiece(left, right, operator, src))
        
        # swap operands
        x_incorrect = right_vector + left_vector + operator_vector + right_type_vector + left_type_vector + parent_vector + grand_parent_vector
        y_incorrect = [1]
        xs.append(x_incorrect)
        ys.append(y_incorrect)
        code_pieces.append(CodePiece(right, left, operator, src))
        
    def anomaly_score(self, y_prediction_orig, y_prediction_changed):
        return y_prediction_orig - y_prediction_changed # higher means more likely to be anomaly in current code
    
    def normal_score(self, y_prediction_orig, y_prediction_changed):
        return y_prediction_changed - y_prediction_orig # higher means more likely to be correct in current code  