'''
Created on Apr 9, 2018

@author: Michael Pradel
'''

import Util
from collections import Counter
import random

name_embedding_size = 200
type_embedding_size = 5
max_nb_args = 2

class CodePiece(object):
    def __init__(self, callee, arguments, src):
        self.callee = callee
        self.arguments = arguments
        self.src = src
    
    def to_message(self):
        return str(self.src) + " | " + str(self.callee) + " | " + str(self.arguments)
        
class LearningData(object):
    def __init__(self):
        self.stats = {"calls": 0, "calls_with_too_many_args": 0, "calls_with_too_few_args": 0, "calls_with_known_names": 0,
                      "calls_with_known_base_object": 0}
    
    def pre_scan(self, training_data_paths, validation_data_paths):
        print("Stats on training data")
        self.gather_stats(training_data_paths)
        print("Stats on validation data")
        self.gather_stats(validation_data_paths)

    def gather_stats(self, data_paths):
        callee_to_freq = Counter()
        argument_to_freq = Counter()
        total_calls = 0
        
        for call in Util.DataReader(data_paths):
            callee_to_freq[call["callee"]] += 1
            for argument in call["arguments"]:
                argument_to_freq[argument] += 1
            total_calls += 1
        
        print("Total calls           : " + str(total_calls))    
        print("Unique callees        : " + str(len(callee_to_freq)))
        print("  " + "\n  ".join(str(x) for x in callee_to_freq.most_common(10)))
        Util.analyze_histograms(callee_to_freq)
        print("Unique arguments      : " + str(len(argument_to_freq)))
        print("  " + "\n  ".join(str(x) for x in argument_to_freq.most_common(10)))
        Util.analyze_histograms(argument_to_freq)
        
    def code_to_xy_pairs(self, call, xs, ys, name_to_vector, type_to_vector, node_type_to_vector, calls=None):
        arguments = call["arguments"]
        self.stats["calls"] += 1
        if len(arguments) > max_nb_args:
            self.stats["calls_with_too_many_args"] += 1
            return
        if len(arguments) < 1:
            self.stats["calls_with_too_few_args"] += 1
            return
        
        # mandatory information: callee and argument names
        callee_string = call["callee"]
        argument_strings = call["arguments"]
        if not (callee_string in name_to_vector):
            return
        for argument_string in argument_strings:
            if not (argument_string in name_to_vector):
                return
        self.stats["calls_with_known_names"] += 1
        callee_vector = name_to_vector[callee_string]
        argument_vectors = []
        for argument_string in argument_strings:
            argument_vectors.append(name_to_vector[argument_string])
            if len(argument_vectors) >= max_nb_args:
                break
        
        # optional information: base object, argument types, etc.
        base_string = call["base"]
        base_vector = name_to_vector.get(base_string, [0]*name_embedding_size)
        if base_string in name_to_vector:
            self.stats["calls_with_known_base_object"] += 1
        
        argument_type_strings = call["argumentTypes"]
        argument_type_vectors = []
        for argument_type_string in argument_type_strings:
            argument_type_vectors.append(type_to_vector.get(argument_type_string, [0]*type_embedding_size))
            if len(argument_type_vectors) >= max_nb_args:
                break
        
        parameter_strings = call["parameters"]
        parameter_vectors = []
        for parameter_string in parameter_strings:
            parameter_vectors.append(name_to_vector.get(parameter_string, [0]*name_embedding_size))
            if len(parameter_vectors) >= max_nb_args:
                break
        
        # for all xy-pairs: y value = probability that incorrect
        x_orig = callee_vector + base_vector  
        # add argument vectors (and pad if not enough available)
        for i in range(max_nb_args):
            if len(argument_vectors) > i:
                x_orig += argument_vectors[i]
            else:
                x_orig += [0]*name_embedding_size
        # add argument type vectors (and pad if not enough available)
        for i in range(max_nb_args):
            if len(argument_type_vectors) > i:
                x_orig += argument_type_vectors[i]
            else:
                x_orig += [0]*type_embedding_size
        # add parameter vectors (and pad if not enough available)
        for i in range(max_nb_args):
            if len(parameter_vectors) > i:
                x_orig += parameter_vectors[i]
            else:
                x_orig += [0]*name_embedding_size
        y_orig = [0]
        xs.append(x_orig)
        ys.append(y_orig)
        if calls != None:
            calls.append(CodePiece(callee_string, argument_strings, call["src"]))
        
        # for the negative example, remove a randomly picked argument
        idx_to_remove = random.randint(0, len(argument_vectors)-1)
        del argument_vectors[idx_to_remove]
        del argument_type_vectors[idx_to_remove]
        del parameter_vectors[idx_to_remove]
        x_buggy = callee_vector + base_vector
        # add argument vectors (and pad if not enough available)
        for i in range(max_nb_args):
            if len(argument_vectors) > i:
                x_buggy += argument_vectors[i]
            else:
                x_buggy += [0]*name_embedding_size
        # add argument type vectors (and pad if not enough available)
        for i in range(max_nb_args):
            if len(argument_type_vectors) > i:
                x_buggy += argument_type_vectors[i]
            else:
                x_buggy += [0]*type_embedding_size
        # add parameter vectors (and pad if not enough available)
        for i in range(max_nb_args):
            if len(parameter_vectors) > i:
                x_buggy += parameter_vectors[i]
            else:
                x_buggy += [0]*name_embedding_size
        y_buggy = [1]
        
        xs.append(x_buggy)
        ys.append(y_buggy)
        if calls != None:
            calls.append(CodePiece(callee_string, argument_strings, call["src"]))
            
    def anomaly_score(self, y_prediction_orig, y_prediction_changed):
        return y_prediction_orig # higher means more likely to be anomaly in current code
    
    def normal_score(self, y_prediction_orig, y_prediction_changed):
        return y_prediction_changed # higher means more likely to be correct in current code
