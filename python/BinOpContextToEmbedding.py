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

node_type_embedding_size = 8 # if changing here, then also change in LearningDataBinOperator

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
    # arguments: <binOp data files>
    
    data_paths = sys.argv[1:]
    node_type_to_vector = dict()
    node_type_embeddings = set()
    for bin_op in Util.DataReader(data_paths):
        node_types = [bin_op["parent"], bin_op["grandParent"]]
        for node_type in node_types:
            if not (node_type in node_type_to_vector):
                type_embedding = create_random_embedding(node_type_embedding_size, node_type_embeddings)
                node_type_to_vector[node_type] = type_embedding

    time_stamp = math.floor(time.time() * 1000)
    node_type_to_vector_file = "node_type_to_vector_" + str(time_stamp) + ".json"
    with open(node_type_to_vector_file, "w") as file:
        json.dump(node_type_to_vector, file, sort_keys=True, indent=4)
    
    
    