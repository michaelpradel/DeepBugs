'''
Created on Jun 30, 2017

@author: Michael Pradel
'''

import sys
import json
from os.path import join
from os import getcwd
from collections import Counter
import math
import numpy as np
import time
from multiprocessing import Pool

kept_main_tokens = 10000
kept_context_tokens = 1000
context_length = 20

nb_processes = 30

class RawDataReader(object):
    def __init__(self, data_paths):
        self.data_paths = data_paths
         
    def __iter__(self):
        for data_path in self.data_paths:
            print("Reading file " + data_path)
            with open(data_path) as file:
                tokens = json.load(file)
                yield tokens

#standard_tokens = set(["[",  "]",  "{",  "}",  "(",  ")",  ",",  ";",  ":",  ".",  "?",  "=>",  "template",  "...",  "`",  "${",  "=",  "_=",  "++",  "--",  "prefix",  "||",  "&&",  "|",  "^",  "&",  "==",  "!=",  "<",  ">",  "<<",  ">>",  "+",  "-",  "%",  "*",  "/",  "**",  "break",  "case",  "catch",  "continue",  "debugger",  "default",  "do",  "else",  "finally",  "for",  "function",  "if",  "return",  "switch",  "throw",  "try",  "var",  "const",  "while",  "with",  "new",  "this",  "super",  "class",  "extends",  "export",  "import",  "null",  "true",  "false",  "in",  "instanceof",  "typeof",  "void",  "delete"])  

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

def save_token_numbers(token_to_number):
    time_stamp = math.floor(time.time() * 1000)
    file_name = "token_to_number_" + str(time_stamp) + ".json"
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

if __name__ == '__main__':
    # arguments: <list of .json files with tokens and contexts> 
    
    all_raw_data_paths = list(map(lambda f: join(getcwd(), f), sys.argv[1:]))
    print("Total files: "+str(len(all_raw_data_paths))) 
  
    # gather tokens (in parallel)
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
                for context_token in context:
                    context_tokens[context_token] += 1
        return (main_tokens, context_tokens)    

    pool = Pool(processes=nb_processes)
    chunksize = round(len(all_raw_data_paths) / nb_processes)
    if chunksize == 0:
        chunksize = len(all_raw_data_paths)
    counters = pool.map(count_tokens, chunks(all_raw_data_paths, chunksize))
    
    # merge counters that were gathered in parallel
    print("Merging counters...")
    all_main_tokens = Counter()
    all_context_tokens = Counter()
    for main_tokens, context_tokens in counters:
        all_main_tokens.update(main_tokens)
        all_context_tokens.update(context_tokens)
    print("Done with merging counters")
    
    # analyze histograms
    print("Unique main tokens: " + str(len(all_main_tokens)))
    print("  " + "\n  ".join(str(x) for x in all_main_tokens.most_common(20)))
    analyze_histograms(all_main_tokens)
    print()
    print("Unique context tokens: " + str(len(all_context_tokens)))
    print("  " + "\n  ".join(str(x) for x in all_context_tokens.most_common(20)))
    analyze_histograms(all_context_tokens)
    
    # replace infrequent tokens w/ placeholder and write number-encoded tokens + contexts to files
    frequent_main_tokens = frequent_tokens(all_main_tokens, kept_main_tokens)
    frequent_context_tokens = frequent_tokens(all_context_tokens, kept_context_tokens)
    
    save_token_numbers(frequent_main_tokens)

    # parallelize the encoding
    def encode_tokens_with_context(data_paths):
        print("Data encoding worker called with "+str(len(data_paths))+" files")
        reader = RawDataReader(data_paths)
        encoded_tokens_with_context = []
        for tokens_with_context in reader:
            # replace infrequent tokens with "unknown"
            for token_with_context in tokens_with_context:
                token = token_with_context["token"]
                # first element = number of main tokens
                encoded_main_token = encode(frequent_main_tokens, token)
                if encoded_main_token != 0:  # ignore "unknown" tokens (encoded as 0)
                    encoded = np.empty(context_length + 1, dtype=int)
                    encoded[0] = encoded_main_token
                
                    context = token_with_context["context"]
                    idx = 1
                    for context_token in context:
                        # 2nd, 3rd, etc. element = numbers of context tokens
                        encoded[idx] = encode(frequent_context_tokens, context_token)
                        idx += 1
                    
                    encoded_tokens_with_context.append(encoded)
                
                    # occasionally save and forget (to avoid filling up all memory)
                    if len(encoded_tokens_with_context) % 1000000 is 0:
                        file_name = save_tokens_with_context(encoded_tokens_with_context)
                        print("Have written data to " + file_name)
            
                        encoded_tokens_with_context = []
            
        file_name = save_tokens_with_context(encoded_tokens_with_context)
        print("Have written data to " + file_name)
    
    print("Encoding data and written it to files...")
    pool = Pool(processes=nb_processes)
    pool.map(encode_tokens_with_context, chunks(all_raw_data_paths, chunksize))
    
    print("Done")
        
            
    
    