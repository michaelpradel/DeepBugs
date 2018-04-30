'''
Created on Jul 26, 2017

@author: Michael Pradel
'''

import math
from os import getcwd
from os.path import join
import sys
import time
import json
from gensim.models import Word2Vec

nb_tokens_in_context = 20
kept_tokens = 10000

embedding_size = 200

class EncodedSequenceReader(object):
    def __init__(self, data_paths):
        self.data_paths = data_paths
        
    def __iter__(self):
        for data_path in self.data_paths:
            print("Reading file " + data_path)
            with open(data_path) as file:
                token_sequences = json.load(file)
            for seq in token_sequences:
                yield seq

if __name__ == '__main__':
    # arguments: <token_to_nb_file> <list of .json files with tokens>
    
    token_to_nb_file = sys.argv[1]
    data_paths = list(map(lambda f: join(getcwd(), f), sys.argv[2:]))
    if len(data_paths) is 0:
        print("Must pass token_to_nb files and at least one data file")
        sys.exit(1)

    token_seqs = EncodedSequenceReader(data_paths)
    model = Word2Vec(token_seqs, min_count=1, window=nb_tokens_in_context/2, size=embedding_size, workers=40)

    # store the model
    time_stamp = math.floor(time.time() * 1000)
    model.save("embedding_model_" + str(time_stamp))

    # after training the model, write token-to-vector map (= learned embedding) to file
    with open(token_to_nb_file, "r") as file:
        token_to_nb = json.load(file)
    token_to_vector = dict()
    for token in model.wv.vocab:
        if token.startswith("ID:") or token.startswith("LIT:"):
            vector = model[token].tolist()
            token_to_vector[token] = vector
    token_to_vector_file_name = "token_to_vector_" + str(time_stamp) + ".json"
    with open(token_to_vector_file_name, "w") as file:
        json.dump(token_to_vector, file, sort_keys=True, indent=4)
       
    