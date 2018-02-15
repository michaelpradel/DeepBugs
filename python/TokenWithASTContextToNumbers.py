'''
Created on Jul 20, 2017

@author: Michael Pradel
'''

import sys
import json
from os.path import join
from os import getcwd
from os import listdir
from collections import Counter
import math
import numpy as np
import time
from multiprocessing import Pool
import random

MAX_CONTEXT_TOKENS_PER_CATEGORY = 10

kinds_of_context = ["parent", "grandParent", "siblings", "uncles", "cousins", "nephews"]
kinds_of_context_lists = ["siblings", "uncles", "cousins", "nephews"]

class RawDataReader(object):
    def __init__(self, data_paths):
        self.data_paths = data_paths
         
    def __iter__(self):
        for data_path in self.data_paths:
            print("Reading file " + data_path)
            with open(data_path, encoding="utf8") as file:
                items = json.load(file)
                yield items

def count_tokens(data_paths):
    print("Worker starting to read "+str(len(data_paths))+" files")
    reader = RawDataReader(data_paths)
    main_tokens = Counter()
    context_tokens = Counter()
    for tokens_with_context in reader:
        for token_with_context in tokens_with_context:
            token = token_with_context["token"]
            context = token_with_context["context"]
            main_tokens[token] += 1
            for kind_of_context in kinds_of_context:
                if isinstance(context[kind_of_context], str):
                    context_tokens[context[kind_of_context]] += 1
                else:
                    for token in context[kind_of_context]:
                        context_tokens[token] += 1
    return (main_tokens, context_tokens)   


# parallelize the encoding
def encode_tokens_with_context(data_paths, frequent_tokens):

    frequent_main_tokens, frequent_context_tokens = frequent_tokens
    print("Data encoding worker called with "+str(len(data_paths))+" files")
    reader = RawDataReader(data_paths)
    encoded_tokens_with_context = []
    for tokens_with_context in reader:
        # replace infrequent tokens with "unknown"
        for token_with_context in tokens_with_context:
            token = token_with_context["token"]
            # encoding:
            #  - first element  = number of main token
            #  - second element = number of parent token
            #  - third element  = position in parent
            #  - fourth element = number of grand parent token
            #  - fifth element  = position in grand parent
            #  - next MAX_CONTEXT_TOKENS_PER_CATEGORY elements = numbers of sibling tokens
            #  - next MAX_CONTEXT_TOKENS_PER_CATEGORY elements = numbers of uncle tokens
            #  - next MAX_CONTEXT_TOKENS_PER_CATEGORY elements = numbers of cousin tokens
            #  - next MAX_CONTEXT_TOKENS_PER_CATEGORY elements = numbers of nephew tokens
            # total nb of elements: 5 + 4 * MAX_CONTEXT_TOKENS_PER_CATEGORY
            encoded_main_token = encode(frequent_main_tokens, token)
            if encoded_main_token != 0:  # ignore "unknown" tokens (encoded as 0)
                encoded = np.empty(5 + 4 * MAX_CONTEXT_TOKENS_PER_CATEGORY, dtype=int)
                encoded[0] = encoded_main_token
            
                context = token_with_context["context"]
                encoded[1] = encode(frequent_context_tokens, context["parent"])
                encoded[2] = context["positionInParent"]
                encoded[3] = encode(frequent_context_tokens, context["grandParent"])
                encoded[4] = context["positionInGrandParent"]
                next_idx = 5
                for kind_of_context in kinds_of_context_lists:
                    remaining_slots = MAX_CONTEXT_TOKENS_PER_CATEGORY
                    for token in context[kind_of_context]:
                        encoded[next_idx] = encode(frequent_context_tokens, token)
                        next_idx += 1
                        remaining_slots -= 1
                        if remaining_slots == 0:
                            break
                    for _ in range(0, remaining_slots):
                        encoded[next_idx] = -1
                        next_idx += 1
                
                encoded_tokens_with_context.append(encoded)
            
                # occasionally save and forget (to avoid filling up all memory)
                if len(encoded_tokens_with_context) % 1000000 is 0:
                    file_name = save_tokens_with_context(encoded_tokens_with_context)
                    print("Have written data to " + file_name)
        
                    encoded_tokens_with_context = []
        
    file_name = save_tokens_with_context(encoded_tokens_with_context)
    print("Have written data to " + file_name)

def analyze_histograms(all_tokens):
    total = sum(all_tokens.values())
    sorted_pairs = all_tokens.most_common()
    percentages_to_cover = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
    nb_covered = 0
    pairs_covered = 0
    for pair in sorted_pairs:
        nb_covered += pair[1]
        pairs_covered += 1
        percentage_covered = (nb_covered * 1.0) / total
        done = False
        while not done and len(percentages_to_cover) > 0:
            next_percentage = percentages_to_cover[0]
            if percentage_covered >= next_percentage:
                print(str(pairs_covered) + " most frequent terms cover " + str(next_percentage) + " of all terms") 
                percentages_to_cover = percentages_to_cover[1:]
            else:
                done = True

def save_tokens_with_context(encoded_tokens_with_context):
    all_data = np.asarray(encoded_tokens_with_context)
    
    time_stamp = math.floor(time.time() * 1000)
    file_name = "encoded_tokens_with_context_" + str(time_stamp) + ".npy"
    np.save(file_name, all_data)
    return file_name

def save_token_numbers(token_to_number, prefix):
    time_stamp = math.floor(time.time() * 1000)
    file_name = prefix + "_token_to_number_" + str(time_stamp) + ".json"
    with open(file_name, 'w') as file:
        json.dump(token_to_number, file, sort_keys=True, indent=4)

unknown = "@@~UNKNOWN~@@" # represented by 0
def frequent_tokens(counter, nb_tokens): 
    token_to_number = dict()
    ctr = 1 # reserve 0 for "unknown"
    for pair in counter.most_common(nb_tokens):
        token_to_number[pair[0]] = ctr
        ctr += 1
    return token_to_number

def encode(frequent_to_number, token):
    if token in frequent_to_number:
        return frequent_to_number[token]
    else:
        return 0

def chunks(li, n):
    for i in range(0, len(li), n):
        yield li[i:i + n]
