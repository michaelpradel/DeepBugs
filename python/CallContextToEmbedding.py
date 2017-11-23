'''
Created on Oct 31, 2017

@author: Michael Pradel
'''

import json
import math
import sys
import time

import random

import Util

# if changing the following, also change in AnomalyDetector
filename_embedding_size = 50
type_embedding_size = 5

def create_random_embedding(size, used_embeddings):
    while True:
        embedding = []
        for _ in range(0, size):
            random_bit = round(random.random())
            embedding.append(random_bit)
        if not (str(embedding) in used_embeddings):
            used_embeddings.add(str(embedding))
            return embedding

if __name__ == '__main__':
    # arguments: <call data files>
    
    call_data_paths = sys.argv[1:]
    filename_to_vector = dict()
    type_to_vector = dict()
    filename_embeddings = set()
    type_embeddings = set()
    for call in Util.DataReader(call_data_paths):
        filename = call["filename"]
        if not (filename in filename_to_vector):
            filename_embedding = create_random_embedding(filename_embedding_size, filename_embeddings)
            filename_to_vector[filename] = filename_embedding
        argument_types = call["argumentTypes"]
        for argument_type in argument_types:
            if not (argument_type in type_to_vector):
                type_embedding = create_random_embedding(type_embedding_size, type_embeddings)
                type_to_vector[argument_type] = type_embedding

    time_stamp = math.floor(time.time() * 1000)
    filename_to_vector_file = "filename_to_vector_" + str(time_stamp) + ".json"
    with open(filename_to_vector_file, "w") as file:
        json.dump(filename_to_vector, file, sort_keys=True, indent=4)
    type_to_vector_file = "type_to_vector_" + str(time_stamp) + ".json"
    with open(type_to_vector_file, "w") as file:
        json.dump(type_to_vector, file, sort_keys=True, indent=4)
        
    
    
    