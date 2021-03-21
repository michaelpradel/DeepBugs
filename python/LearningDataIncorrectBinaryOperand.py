'''
Created on Nov 13, 2017

@author: Michael Pradel, Sabine Zach
'''

import Util
from collections import namedtuple
import random

from HyperParameters import type_embedding_size

operator_embedding_size = 30  # the number should correspond to the maximum
# length of the operator vector
# if not set, it could accidently happen, that
# the operator vector is to short
# and as a result is not compatible with the model!


class CodePiece(object):
    def __init__(self, left, right, op, src):
        self.left = left
        self.right = right
        self.op = op
        self.src = src

    def to_message(self):
        return str(self.src) + " | " + str(self.left) + " | " + str(self.op) + " | " + str(self.right)


Operand = namedtuple('Operand', ['op', 'type'])


class LearningData(object):
    def __init__(self):
        self.file_to_operands = dict()  # string to set of Operands
        self.stats = {}

    def resetStats(self):
        self.stats = {}

    def pre_scan(self, first_data_paths, second_data_paths=[]):
        all_operators_set = set()
        for bin_op in Util.DataReader(first_data_paths):
            file = bin_op["src"].split(" : ")[0]
            operands = self.file_to_operands.setdefault(file, set())
            left_operand = Operand(bin_op["left"], bin_op["leftType"])
            right_operand = Operand(bin_op["right"], bin_op["rightType"])
            operands.add(left_operand)
            operands.add(right_operand)

            all_operators_set.add(bin_op["op"])
        if second_data_paths == []:
            self.all_operators = list(all_operators_set)
            return

        for bin_op in Util.DataReader(second_data_paths):
            file = bin_op["src"].split(" : ")[0]
            operands = self.file_to_operands.setdefault(file, set())
            left_operand = Operand(bin_op["left"], bin_op["leftType"])
            right_operand = Operand(bin_op["right"], bin_op["rightType"])
            operands.add(left_operand)
            operands.add(right_operand)

            all_operators_set.add(bin_op["op"])
        self.all_operators = list(all_operators_set)

    def code_to_xy_pairs(self, gen_negatives, bin_op, xs, ys, name_to_vector, type_to_vector, node_type_to_vector, code_pieces):
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

        left_vector = name_to_vector[left]
        right_vector = name_to_vector[right]
        operator_vector = [0] * operator_embedding_size
        operator_vector[self.all_operators.index(operator)] = 1
        left_type_vector = type_to_vector.get(
            left_type, [0]*type_embedding_size)
        right_type_vector = type_to_vector.get(
            right_type, [0]*type_embedding_size)
        parent_vector = node_type_to_vector[parent]
        grand_parent_vector = node_type_to_vector[grand_parent]

        # for all xy-pairs: y value = probability that incorrect
        x_correct = left_vector + right_vector + operator_vector + \
            left_type_vector + right_type_vector + parent_vector + grand_parent_vector
        y_correct = [0]
        xs.append(x_correct)
        ys.append(y_correct)
        code_pieces.append(CodePiece(left, right, operator, src))

        # generate negatives: find an alternative operand in the same file
        if gen_negatives:
            replace_left = random.random() < 0.5
            if replace_left:
                to_replace_operand = left
            else:
                to_replace_operand = right
            file = src.split(" : ")[0]
            all_operands = self.file_to_operands[file]
            tries_left = 100
            found = False
            while (not found) and tries_left > 0:
                other_operand = random.choice(list(all_operands))
                if other_operand.op in name_to_vector and other_operand.op != to_replace_operand:
                    found = True
                tries_left -= 1

            if not found:
                xs.pop()
                ys.pop()
                code_pieces.pop()
                return

            other_operand_vector = name_to_vector[other_operand.op]
            other_operand_type_vector = type_to_vector[other_operand.type]
            # replace one operand with the alternative one
            if replace_left:
                x_incorrect = other_operand_vector + right_vector + operator_vector + \
                    other_operand_type_vector + right_type_vector + \
                    parent_vector + grand_parent_vector
            else:
                x_incorrect = left_vector + other_operand_vector + operator_vector + \
                    right_type_vector + other_operand_type_vector + \
                    parent_vector + grand_parent_vector
            y_incorrect = [1]
            xs.append(x_incorrect)
            ys.append(y_incorrect)
            code_pieces.append(CodePiece(right, left, operator, src))

    def anomaly_score(self, y_prediction_orig, y_prediction_changed):
        return y_prediction_orig

    def normal_score(self, y_prediction_orig, y_prediction_changed):
        return y_prediction_changed
