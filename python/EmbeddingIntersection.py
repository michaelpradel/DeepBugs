'''
Created on Aug 16, 2020

@author: Michael Pradel
'''

import sys
import json


if __name__ == "__main__":
    # arguments: <list of .json files that map tokens to vectors>

    in_files = sys.argv[1:]

    # read embeddings
    inputs = []
    for file_name in in_files:
        with open(file_name, "r") as fp:
            token_to_vector = json.load(fp)
            print(f"Read {len(token_to_vector)} embeddings from {file_name}")
        inputs.append(token_to_vector)
    
    # compute intersection
    token_union = set()
    for token_to_vector in inputs:
        token_union.update(token_to_vector.keys())
    token_intersection = set()
    for token in token_union:
        keep = True
        for token_to_vector in inputs:
            if not token in token_to_vector:
                keep = False
                continue
        if keep:
            token_intersection.add(token)

    print(f"Found {len(token_intersection)} common tokens")
    # write embeddings w/ common tokens only
    for input_idx, token_to_vector in enumerate(inputs):
        reduced_token_to_vector = {}
        for token, vector in token_to_vector.items():
            if token in token_intersection:
                reduced_token_to_vector[token] = vector
        
        out_file_name = f"{in_files[input_idx][:-5]}_common.json"
        with open(out_file_name, "w") as fp:
            json.dump(reduced_token_to_vector, fp, sort_keys=True, indent=4)
            print(f"Wrote {len(reduced_token_to_vector)} to {out_file_name}")

