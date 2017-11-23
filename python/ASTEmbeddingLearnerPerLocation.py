'''
Created on Jul 20, 2017

@author: Michael Pradel
'''

import json
import math
from os import getcwd
from os.path import join
import sys
import time

from keras.layers.core import Dense
from keras.models import Model
from keras.models import Sequential

import numpy as np
import random
from collections import namedtuple
import Util

kept_main_tokens = 10000
kept_context_tokens = 1000
max_context_tokens_per_category = 10  # when changing, also change in TokenWithASTContextToNumbers

embedding_size = 200
batch_size = 50
nb_epochs = 2
sampling_rate = 1

def count_samples(data_paths):
    total_examples = 0
    for path in data_paths:
        encoded_tokens_with_context = np.load(path)
        total_examples += len(encoded_tokens_with_context)
    return total_examples

def xy_pair_generator(data_paths, expected_x_length, expected_y_length, only_once=False):
    done = False
    while not done:
        for path in data_paths:
            encoded_tokens_with_context = np.load(path)
            for token_with_context in encoded_tokens_with_context:
                sample = random.random() < sampling_rate
                if sample:
                    # given encoding:
                    #  - 0. element  = location id
                    #  - 1. element  = number of main token
                    #  - 2. element = number of parent token
                    #  - 3. element  = position in parent
                    #  - 4. element = number of grand parent token
                    #  - 5. element  = position in grand parent
                    #  - next max_context_tokens_per_category elements = numbers of sibling tokens
                    #  - next max_context_tokens_per_category elements = numbers of uncle tokens
                    #  - next max_context_tokens_per_category elements = numbers of cousin tokens
                    #  - next max_context_tokens_per_category elements = numbers of nephew tokens
                    # representation to produce:
                    #  - main token: one-hot vector
                    #  - context vector: concatenation of subvectors:
                    #    - parent subvector: one-hot vector
                    #    - position in parent subvector: single number
                    #    - grand parent subvector: one-hot vector
                    #    - position in grand parent subvector: single number
                    #    - four subvectors for siblings, uncles, cousins, and nephews: each is a k-hot vector
                    location = token_with_context[0]
                    
                    main_vector = np.zeros(kept_main_tokens + 1)
                    main_vector[token_with_context[1]] = 1
                    assert len(main_vector) == expected_y_length, str(len(main_vector)) + " is not " + str(expected_y_length) 
                    
                    x_length = (kept_context_tokens + 1) + 2
                    context_vector = np.zeros(x_length)
                    # parent
                    hot_element = token_with_context[2]
                    context_vector[hot_element] = 1
                    position_in_parent = token_with_context[3]
                    context_vector[kept_context_tokens + 1] = position_in_parent
                    # grand parent
                    hot_element = token_with_context[4]
                    context_vector[hot_element] = 1
                    position_in_parent = token_with_context[5]
                    context_vector[kept_context_tokens + 2] = position_in_parent
                    
                    for kind_nb in range(0,4): # do four times the same: for siblings, uncles, cousins, and nephews
                        for hot_element in token_with_context[6 + (max_context_tokens_per_category * kind_nb):5 + (max_context_tokens_per_category * (kind_nb + 1))]:
                            if hot_element > -1:
                                context_vector[hot_element] = 1
                    
                    assert len(context_vector) == expected_x_length, len(context_vector)

                    yield (context_vector, main_vector, location)
        done = only_once

def batch_generator(xy_pair_generator):
    xs = []
    ys = []
    for x, y, _ in xy_pair_generator:
        xs.append(x)
        ys.append(y)
        if len(xs) is batch_size:
            batch = (np.asarray(xs), np.asarray(ys))
            yield batch
            xs = []
            ys = []

if __name__ == '__main__':
    # arguments: <main_token_to_nb_file> <context_token_to_nb_file> <list of files with tokens and contexts>
    
    # load main tokens
    main_token_to_nb_file = sys.argv[1]
#     with open(main_token_to_nb_file) as file:
#         main_token_to_nb = json.load(file)
#     nb_to_main_token = {v: k for k, v in main_token_to_nb.items()}
    # load context tokens (for debugging only)
#     context_token_to_nb_file = sys.argv[2]
#     with open(context_token_to_nb_file) as file:
#         context_token_to_nb = json.load(file)
#     nb_to_context_token = {v: k for k, v in context_token_to_nb.items()}

    data_paths = list(map(lambda f: join(getcwd(), f), sys.argv[3:]))
    if len(data_paths) is 0:
        print("Must pass token_to_nb files and at least one data file")
        sys.exit(1)

    x_length = (kept_context_tokens + 1) + 2
    y_length = kept_main_tokens + 1
    total_examples = count_samples(data_paths)
    total_samples = total_examples * sampling_rate
    
    print("Total samples: " + str(total_examples))
    print("Will sample about " + str(total_samples))
    
    # some statistics to better understand the data
    token_to_contexts = dict()
    token_to_occurrences = dict()
    all_contexts = set()
    for context_list, token_list, loc in xy_pair_generator(data_paths, x_length, y_length, only_once=True):
        context = tuple(context_list)
        token = tuple(token_list)
        token_to_contexts.setdefault(token, set()).add(context)
        token_to_occurrences[token] = token_to_occurrences.setdefault(token, 0) + 1
        all_contexts.add(context)
    print("Unique contexts: "+str(len(all_contexts))+" for "+str(total_examples)+" locations")
    Token = namedtuple("Token", ["nbOccurrences", "nbUniqueContexts", "inGroupSimil", "outGroupSimil", "similFactor"])
    all_tokens = []
    uniqueness_scores = []
    total_considered = 0
    for token, contexts in token_to_contexts.items():
        if len(contexts) > 100:
            in_group_simil = Util.in_group_similarity(contexts)
            out_group_simil = Util.out_group_similarity(contexts, all_contexts)
            simil_factor = in_group_simil / out_group_simil
            t = Token(token_to_occurrences[token], len(contexts), round(in_group_simil,3), round(out_group_simil,3), round(simil_factor,3))
            all_tokens.append(t)
            if t.nbOccurrences == 1:
                uniqueness_scores.append(1.0)
            else:
                uniqueness_scores.append((t.nbUniqueContexts - 1) / (t.nbOccurrences - 1))
            total_considered += 1
            if total_considered > 30:
                break
    avg_uniqueness_score = sum(uniqueness_scores)/len(uniqueness_scores)
    print("Average uniqueness score: "+str(round(avg_uniqueness_score, 4)))
    print()
    all_tokens.sort(key=lambda t: t.nbOccurrences, reverse=True)
    for t in all_tokens[:20]:
        print(t)
    
    model = Sequential()
    model.add(Dense(embedding_size, input_shape=(x_length,), name="hidden"))
    model.add(Dense(y_length, activation="sigmoid"))
    
    # using sigmoid for last layer + binary crossentropy because commonly used for multi-label, multi-class classification
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    total_samples_per_epoch = total_samples / batch_size
    validation_samples_per_epoch = total_samples_per_epoch * 0.2    

    generator = batch_generator(xy_pair_generator(data_paths, x_length, y_length))
    model.fit_generator(generator=generator, steps_per_epoch=total_samples_per_epoch, epochs=nb_epochs, validation_steps=validation_samples_per_epoch)

    # store the model
    time_stamp = math.floor(time.time() * 1000) 
    model.save("embedding_model_" + str(time_stamp))

    # after training the model, write location-to-vector map (= learned embedding) to file
    location_to_vector = dict()
    intermediate_layer_model = Model(inputs=model.input, outputs=model.get_layer("hidden").output)
    for x, _, location in xy_pair_generator(data_paths, x_length, y_length, only_once=True):
        intermediate_output = intermediate_layer_model.predict(np.asarray([x]))
        vector = intermediate_output[0].tolist()
        location_to_vector[str(location)] = vector
    location_to_vector_file_name = "location_to_vector_" + str(time_stamp) + ".json"
    with open(location_to_vector_file_name, "w") as file:
        json.dump(location_to_vector, file, sort_keys=True, indent=4)

    # OLD: after training the model, write token-to-vector map (= learned embedding) to file
#     with open(main_token_to_nb_file, "r") as file:
#         token_to_nb = json.load(file)
#     intermediate_layer_model = Model(inputs=model.input, outputs=model.get_layer("hidden").output)
#     token_to_vector = dict()
#     for token, nb in token_to_nb.items():
#         x = [0] * (kept_main_tokens + 1)
#         x[nb] = 1
#         intermediate_output = intermediate_layer_model.predict(np.asarray([x]))
#         vector = intermediate_output[0].tolist()
#         token_to_vector[token] = vector
#     token_to_vector_file_name = "token_to_vector_" + str(time_stamp) + ".json"
#     with open(token_to_vector_file_name, "w") as file:
#         json.dump(token_to_vector, file, sort_keys=True, indent=4)

    # show prediction for a few randomly selected examples
#     ctr = 0
#     for (x,y,loc) in xy_pair_generator(data_paths, x_length, y_length):
#         print("X          : " + str(x))
#         print("Y          : " + str(y))
#         y_predicted = model.predict(x)
#         print("Y_predicted: " + str(y_predicted))
#           
#         ctr += 1
#         if ctr > 10:
#             break
        
    
