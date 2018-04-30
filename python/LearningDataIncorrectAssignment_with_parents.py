'''
Created on Nov 14, 2017

@author: Michael Pradel
'''

import Util
from collections import namedtuple
import random

type_embedding_size = 5

class CodePiece(object):
    def __init__(self, lhs, rhs, src):
        self.lhs = lhs
        self.rhs = rhs
        self.src = src
    
    def to_message(self):
        return str(self.src) + " | " + str(self.lhs) + " | " + str(self.rhs)

RHS = namedtuple('Assignment', ['rhs', 'type'])
    
class LearningData(object):
    def __init__(self):
        self.file_to_RHSs = dict() # string to set of RHSs
        self.stats = {}

    def pre_scan(self, training_data_paths, validation_data_paths):
        for assignment in Util.DataReader(training_data_paths):
            file = assignment["src"].split(" : ")[0]
            rhsides = self.file_to_RHSs.setdefault(file, set())
            rhsides.add(RHS(assignment["rhs"], assignment["rhsType"]))
            
        for assignment in Util.DataReader(validation_data_paths):
            file = assignment["src"].split(" : ")[0]
            rhsides = self.file_to_RHSs.setdefault(file, set())
            rhsides.add(RHS(assignment["rhs"], assignment["rhsType"]))
    
    def code_to_xy_pairs(self, assignment, xs, ys, name_to_vector, type_to_vector, node_type_to_vector, code_pieces):
        lhs = assignment["lhs"]
        rhs = assignment["rhs"]
        rhs_type = assignment["rhsType"]
        parent = assignment["parent"]
        grand_parent = assignment["grandParent"]
        src = assignment["src"]
        if not (lhs in name_to_vector):
            return
        if not (rhs in name_to_vector):
            return
        
        lhs_vector = name_to_vector[lhs]
        rhs_vector = name_to_vector[rhs]
        rhs_type_vector = type_to_vector.get(rhs_type, [0]*type_embedding_size)
        parent_vector = node_type_to_vector[parent]
        grand_parent_vector = node_type_to_vector[grand_parent]
        
        # find an alternative rhs in the same file
        file = src.split(" : ")[0]
        all_RHSs = self.file_to_RHSs[file]
        tries_left = 100
        found = False
        while (not found) and tries_left > 0:
            other_rhs = random.choice(list(all_RHSs))
            if other_rhs.rhs in name_to_vector and other_rhs.rhs != rhs:
                found = True
            tries_left -= 1
            
        if not found:
            return
        
        # for all xy-pairs: y value = probability that incorrect
        x_correct = lhs_vector + rhs_vector + rhs_type_vector + parent_vector + grand_parent_vector
        y_correct = [0]
        xs.append(x_correct)
        ys.append(y_correct)
        code_pieces.append(CodePiece(lhs, rhs, src))
        
        other_rhs_vector = name_to_vector[other_rhs.rhs]
        other_rhs_type_vector = type_to_vector[other_rhs.type]
        x_incorrect = lhs_vector + other_rhs_vector + other_rhs_type_vector + parent_vector + grand_parent_vector
        y_incorrect = [1]
        xs.append(x_incorrect)
        ys.append(y_incorrect)
        code_pieces.append(CodePiece(lhs, rhs, src))
     
    def anomaly_score(self, y_prediction_orig, y_prediction_changed):
        return y_prediction_orig
    
    def normal_score(self, y_prediction_orig, y_prediction_changed):
        return y_prediction_changed   
            