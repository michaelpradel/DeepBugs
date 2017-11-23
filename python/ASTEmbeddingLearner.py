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
from keras import backend as K

import numpy as np
import random

kept_main_tokens = 10000
kept_context_tokens = 1000
max_context_tokens_per_category = 10

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

def xy_pair_generator(data_paths, expected_x_length, expected_y_length):
    while True:
        for path in data_paths:
            encoded_tokens_with_context = np.load(path)
            for token_with_context in encoded_tokens_with_context:
                sample = random.random() < sampling_rate
                if sample:
                    # given encoding:
                    #  - first element  = number of main token
                    #  - second element = number of parent token
                    #  - third element  = position in parent
                    #  - fourth element = number of grand parent token
                    #  - fifth element  = position in grand parent
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
                    x = np.zeros(kept_main_tokens + 1)
                    x[token_with_context[0]] = 1
                    assert len(x) == expected_x_length, str(len(x)) + " is not " + str(expected_x_length) 
                    
                    y_length = 6 * (kept_context_tokens + 1) + 2
                    y = np.zeros(y_length)
                    for idx in [1,3]: # do two times the same: for parent and grand parent
                        hot_element = token_with_context[idx]
                        position_in_parent = token_with_context[idx + 1]
                        offset = (kept_context_tokens + 1) + 1 if idx == 3 else 0
                        y[offset + hot_element] = 1
                        y[offset + kept_context_tokens + 1] = position_in_parent
                    for kind_nb in range(0,4): # do four times the same: for siblings, uncles, cousins, and nephews
                        offset = (2 * (kept_context_tokens + 1)) + 2
                        for hot_element in token_with_context[5 + (max_context_tokens_per_category * kind_nb):5 + (max_context_tokens_per_category * (kind_nb + 1))]:
                            if hot_element > -1:
                                y[offset + hot_element] = 1
                    
                    assert len(y) == expected_y_length, len(y)
                    
                    yield (x, y)
    assert False, "Should never reach this line"

def batch_generator(xy_pair_generator):
    xs = []
    ys = []
    for x, y in xy_pair_generator:
        xs.append(x)
        ys.append(y)
        if len(xs) is batch_size:
            batch = (np.asarray(xs), np.asarray(ys))
            yield batch
            xs = []
            ys = []

if __name__ == '__main__':
    # arguments: <main_token_to_nb_file> <list of files with tokens and contexts>
    
    token_to_nb_file = sys.argv[1]
    data_paths = list(map(lambda f: join(getcwd(), f), sys.argv[2:]))
    if len(data_paths) is 0:
        print("Must pass token_to_nb files and at least one data file")
        sys.exit(1)

    x_length = kept_main_tokens + 1
    y_length = 6 * (kept_context_tokens + 1) + 2
    total_examples = count_samples(data_paths)
    total_samples = total_examples * sampling_rate
    
    print("Total samples: " + str(total_examples))
    print("Will sample about " + str(total_samples))
    
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

    # after training the model, write token-to-vector map (= learned embedding) to file
    with open(token_to_nb_file, "r") as file:
        token_to_nb = json.load(file)
    intermediate_layer_model = Model(inputs=model.input, outputs=model.get_layer("hidden").output)
    token_to_vector = dict()
    for token, nb in token_to_nb.items():
        x = [0] * (kept_main_tokens + 1)
        x[nb] = 1
        intermediate_output = intermediate_layer_model.predict(np.asarray([x]))
        vector = intermediate_output[0].tolist()
        token_to_vector[token] = vector
    token_to_vector_file_name = "token_to_vector_" + str(time_stamp) + ".json"
    with open(token_to_vector_file_name, "w") as file:
        json.dump(token_to_vector, file, sort_keys=True, indent=4)

    # show prediction for a few randomly selected examples
#     ctr = 0
#     for (x,y) in xy_pair_generator(data_paths, x_length, y_length):
#         print("X          : " + str(x))
#         print("Y          : " + str(y))
#         y_predicted = model.predict(x)
#         print("Y_predicted: " + str(y_predicted))
#         
#         ctr += 1
#         if ctr > 10:
#             break
        
    
    
    
    
