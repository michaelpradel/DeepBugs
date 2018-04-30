'''
Created on Jul 26, 2017

@author: Michael Pradel
'''

import sys
import json
from os.path import join
from os import getcwd
from collections import Counter
import math
import time
from multiprocessing import Pool

kept_tokens = 10000

nb_processes = 30

class RawDataReader(object):
    def __init__(self, data_paths):
        self.data_paths = data_paths
         
    def __iter__(self):
        for data_path in self.data_paths:
            print("Reading file " + data_path)
            with open(data_path) as file:
                token_sequences = json.load(file)
                for seq in token_sequences:
                    yield seq

def analyze_histograms(all_tokens):
    total = sum(all_tokens.values())
    sorted_pairs = all_tokens.most_common()
    percentages_to_cover = list(map(lambda x: x/100.0,range(1,100)))  #[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
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
                
    covered_by_kept_tokens = 0
    for pair in sorted_pairs[:kept_tokens]:
        covered_by_kept_tokens += pair[1]
    perc_covered_by_kept_tokens = (covered_by_kept_tokens * 1.0) / total
    print("----")
    print(str(covered_by_kept_tokens) + " most frequent terms cover " + str(perc_covered_by_kept_tokens) + " of all terms")

def save_tokens(encoded_tokens):
    time_stamp = math.floor(time.time() * 1000)
    file_name = "encoded_tokens_" + str(time_stamp) + ".json"
    with open(file_name, "w") as file:
        json.dump(encoded_tokens, file, indent=4)
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
        return token
    else:
        return "UNK"

def chunks(li, n):
    for i in range(0, len(li), n):
        yield li[i:i + n]

if __name__ == '__main__':
    # arguments: <list of .json files with tokens> 
    
    all_raw_data_paths = list(map(lambda f: join(getcwd(), f), sys.argv[1:]))
    print("Total files: "+str(len(all_raw_data_paths))) 
  
    # gather tokens (in parallel)
    def count_tokens(data_paths):
        print("Worker starting to read "+str(len(data_paths))+" files")
        reader = RawDataReader(data_paths)
        tokens = Counter()
        for token_seq in reader:
            for token in token_seq:
                tokens[token] += 1
        return tokens    

    pool = Pool(processes=nb_processes)
    chunksize = round(len(all_raw_data_paths) / nb_processes)
    if chunksize == 0:
        chunksize = len(all_raw_data_paths)
    counters = pool.map(count_tokens, chunks(all_raw_data_paths, chunksize))
    
    # merge counters that were gathered in parallel
    print("Merging counters...")
    all_tokens = Counter()
    for tokens in counters:
        all_tokens.update(tokens)
    print("Done with merging counters")
    
    # analyze histograms
    print()
    print("Unique tokens: " + str(len(all_tokens)))
    print("  " + "\n  ".join(str(x) for x in all_tokens.most_common(20)))
    analyze_histograms(all_tokens)
    print()
    
    # replace infrequent tokens w/ placeholder and write number-encoded tokens + contexts to files
    frequent_tokens = frequent_tokens(all_tokens, kept_tokens)
    
    save_token_numbers(frequent_tokens)

    # parallelize the encoding
    def encode_tokens(data_paths):
        print("Data encoding worker called with "+str(len(data_paths))+" files")
        reader = RawDataReader(data_paths)
        token_ctr = 0
        all_encoded_seqs = []
        for token_seq in reader:
            # replace infrequent tokens with "unknown"
            encoded_token_seq = []
            for t in token_seq:
                encoded_token_seq.append(encode(frequent_tokens, t))
            token_ctr += len(token_seq)
            all_encoded_seqs.append(encoded_token_seq)
            
            # occasionally save and forget (to avoid filling up all memory)
            if token_ctr > 1000000:
                file_name = save_tokens(all_encoded_seqs)
                print("Have written data to " + file_name)
                token_ctr = 0
                all_encoded_seqs = []
            
        file_name = save_tokens(all_encoded_seqs)
        print("Have written data to " + file_name)
    
    print("Encoding data and written it to files...")
    pool = Pool(processes=nb_processes)
    pool.map(encode_tokens, chunks(all_raw_data_paths, chunksize))
    
    print("Done")
        
    