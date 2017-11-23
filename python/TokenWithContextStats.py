'''
Created on Jul 17, 2017

@author: Michael Pradel
'''

from os import getcwd
from os.path import join
import sys

import numpy as np
import json

nb_tokens_in_context = 20

if __name__ == '__main__':
    # arguments: <list of files with tokens and contexts>
    print("Total arguments: "+str(len(sys.argv)))
    data_paths = list(map(lambda f: join(getcwd(), f), sys.argv[1:]))
    print("Total files: "+str(len(data_paths)))
    if len(data_paths) is 0:
        print("Must pass at least one data file")
        sys.exit(1)
        
    token_to_contexts = dict()  # store contexts as set of str(array_of_numbers)
    context_to_tokens = dict()

    visited_files = 0    
    for path in data_paths:
        visited_files += 1
        print("Visiting file "+str(visited_files)+" files of "+str(len(data_paths)))
        encoded_tokens_with_context = np.load(path)
        print("  Tokens with context: "+str(len(encoded_tokens_with_context)))
        visited_tokens = 0
        for token_with_context in encoded_tokens_with_context:
            # first element of token_with_context = number of main token
            token = str(token_with_context[0])
            context_nbs = []
            for nb_of_context_token in token_with_context[1:]: # 2nd, 3rd, etc. element of token_with_context = numbers of context tokens
                context_nbs.append(nb_of_context_token)
            context = str(context_nbs)
            
            # track token-to-context mappings
            if token in token_to_contexts:
                token_to_contexts[token].add(context)
            else:
                token_to_contexts[token] = set([context])
            
            # track context-to-token mappings
            if context in context_to_tokens:
                context_to_tokens[context].add(token)
            else:
                context_to_tokens[context] = set([token])
            
            visited_tokens += 1
            if visited_tokens % 100000 is 0:
                print("  Visited tokens: "+str(visited_tokens))

    # transform sets to lists for serialization & count 1:1 mappings
    serializable_token_to_contexts = dict()
    serializable_context_to_tokens = dict()
    tokens_with_single_context = 0
    contexts_with_single_token = 0
    for token, contexts in token_to_contexts.items():
        serializable_token_to_contexts[token] = list(contexts)
        if len(contexts) is 1:
            tokens_with_single_context += 1
    for context, tokens in context_to_tokens.items():
        serializable_context_to_tokens[context] = list(tokens)
        if len(tokens) is 1:
            contexts_with_single_token += 1
                
    print(str(tokens_with_single_context)+" of "+str(len(token_to_contexts))+" tokens occur in only 1 context")
    print(str(contexts_with_single_token)+" of "+str(len(context_to_tokens))+" contexts occur in only 1 context")
                
    with open("tokens_to_contexts.json", "w") as file:
        json.dump(serializable_token_to_contexts, file, indent=4)
    with open("context_to_tokens.json", "w") as file:
        json.dump(serializable_context_to_tokens, file, indent=4)
                
