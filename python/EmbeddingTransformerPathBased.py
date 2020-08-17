'''
Created on Aug 16, 2020

@author: Michael Pradel
'''

import sys
import json
import math
import time


if __name__ == "__main__":
    # arguments: <token_to_nb_file> <.txt file with path-based embeddings>

    token_to_nb_file = sys.argv[1]
    raw_token_to_vector = sys.argv[2]

    with open(token_to_nb_file, "r") as token_file:
        token_to_nb = json.load(token_file)

    token_to_vector_raw = {}
    with open(raw_token_to_vector, "r") as raw_emb_file:
        line = raw_emb_file.readline()
        while line:
            parts = line.split(" ")
            if len(parts) == 151:
                token = parts[0]
                vector = [float(n) for n in parts[1:]]
                token_to_vector_raw[token] = vector
            line = raw_emb_file.readline()

    token_to_vector = {}
    for token in token_to_nb:
        if token.startswith("ID:"):
            raw_token = token[3:].lower()
        elif token.startswith("LIT:"):
            raw_token = token[4:].lower()
        else:
            continue  # ignore "STD:..." tokens
    
        vector = token_to_vector_raw.get(raw_token)
        if vector is not None:
            token_to_vector[token] = vector

    time_stamp = math.floor(time.time() * 1000)
    token_to_vector_file_name = "token_to_vector_path-based" + str(time_stamp) + ".json"
    with open(token_to_vector_file_name, "w") as file:
        json.dump(token_to_vector, file, sort_keys=True, indent=4)

    missing_tokens = set(token_to_nb.keys()).difference(set(token_to_vector.keys()))
    print(f"{len(missing_tokens)} missing tokens:\n{missing_tokens}")



