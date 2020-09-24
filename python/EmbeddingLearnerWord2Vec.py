'''
Created on Jul 26, 2017

@author: Michael Pradel
'''

from json.decoder import JSONDecodeError
import math
from os import getcwd
from os.path import join
import sys
import time
import json
from gensim.models import Word2Vec
from gensim.models.fasttext import FastText

from HyperParameters import name_embedding_size

nb_tokens_in_context = 20
kept_tokens = 10000




class EncodedSequenceReader(object):
    def __init__(self, data_paths):
        self.data_paths = data_paths

    def __iter__(self):
        for data_path in self.data_paths:
            print("Reading file " + data_path)
            with open(data_path) as file:
                try:
                    token_sequences = json.load(file)
                    for seq in token_sequences:
                        yield seq
                except JSONDecodeError as e:
                    print(
                        f"Warning: Ignoring {data_path} due to JSON decode error")


if __name__ == '__main__':
    # arguments: <token_to_nb_file> <list of .json files with tokens>

    token_to_nb_file = sys.argv[1]
    data_paths = list(map(lambda f: join(getcwd(), f), sys.argv[2:]))
    if len(data_paths) is 0:
        print("Must pass token_to_nb files and at least one data file")
        sys.exit(1)

    token_seqs = EncodedSequenceReader(data_paths)
    # original DeepBugs model (as in OOPSLA'18 paper)
    model = Word2Vec(token_seqs, min_count=1,
                     window=nb_tokens_in_context/2, size=name_embedding_size, workers=40)

    # optimal hyperparameters according to IdBench:
    # w2v-cbow
    # model = Word2Vec(token_seqs, min_count=3, window=5, size=150, workers=40, iter=15, alpha=0.1, sg=0)
    # w2v-sg
    # model = Word2Vec(token_seqs, min_count=3, window=5, size=150, workers=40, iter=15, alpha=0.1, sg=1)
    # FT-cbow
    # model = FastText(token_seqs, min_count=3, window=5, size=150, workers=40, iter=15, alpha=0.1, sg=0)
    # FT-sg
    # model = FastText(token_seqs, min_count=3, window=5, size=150, workers=40, iter=15, alpha=0.1, sg=1)

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
