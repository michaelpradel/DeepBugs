'''
Created on Jul 3, 2017

@author: Michael Pradel
'''

import json
import math
import sys
import time

import numpy as np
import random

from numpy.random import normal

kept_main_tokens = 10000

embedding_size = 200

def count_samples(data_paths):
    total_examples = 0
    for path in data_paths:
        encoded_tokens_with_context = np.load(path)
        total_examples += len(encoded_tokens_with_context)
    return total_examples

def create_random_embedding():
    embedding = []
    for _ in range(0,embedding_size):
#         random_bit = round(random.random())
        random_nb = normal(0.0, 0.7)  # Gaussian distribution that looks roughly like the values in learned embeddings
        embedding.append(random_nb)
    return embedding

if __name__ == '__main__':
    # arguments: <token_to_nb_file> OR <token_to_vector_file>
    
    token_to_nb_file = sys.argv[1]
    with open(token_to_nb_file, "r") as file:
        token_to_nb = json.load(file)
    token_to_vector = dict()
    used_embeddings = set()
    for token, _ in token_to_nb.items():
        done = False
        while not done:
            embedding = create_random_embedding()
            if not (str(embedding) in used_embeddings):
                token_to_vector[token] = embedding
                used_embeddings.add(str(embedding))
                done = True 
    
    time_stamp = math.floor(time.time() * 1000)
    token_to_vector_file_name = "token_to_vector_" + str(time_stamp) + ".json"
    with open(token_to_vector_file_name, "w") as file:
        json.dump(token_to_vector, file, sort_keys=True, indent=4)

    
    
    
    