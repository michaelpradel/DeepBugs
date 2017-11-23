'''
Created on Jul 3, 2017

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

nb_tokens_in_context = 20
kept_main_tokens = 10000
kept_context_tokens = 1000

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
                    # encode token and context as one-hot vectors 
                    # first element of token_with_context = number of main token
                    x = np.zeros(kept_main_tokens + 1)
                    x[token_with_context[0]] = 1
                    assert len(x) == expected_x_length, str(len(x)) + " is not " + str(expected_x_length) 
                    
                    y = np.zeros(nb_tokens_in_context * (kept_context_tokens + 1))
                    for idx, nb_of_context_token in enumerate(token_with_context[1:]): # 2nd, 3rd, etc. element of token_with_context = numbers of context tokens
                        offset = idx * (kept_context_tokens + 1)
                        y[offset + nb_of_context_token] = 1
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

# custom loss and accuracy to account for unbalanced y vectors:
#          
# weight_of_ones = kept_context_tokens
# 
# def weighted_loss(y_true, y_pred):
#     weights = y_true * weight_of_ones
#     clipped_y_pred = K.clip(y_pred, K.epsilon(), None)
#     weighted_cross_entropy = -(y_true * K.log(clipped_y_pred) * weights)
#     result = K.mean(weighted_cross_entropy)
#     return result
#     
# def weighted_accuracy(y_true, y_pred):
#     weights = y_true * weight_of_ones
#     weighted_equal = K.cast(K.equal(y_true, K.round(y_pred)), K.floatx()) * weights
#     return K.mean(weighted_equal)

if __name__ == '__main__':
    # arguments: <token_to_nb_file> <list of files with tokens and contexts>
    
    token_to_nb_file = sys.argv[1]
    data_paths = list(map(lambda f: join(getcwd(), f), sys.argv[2:]))
    if len(data_paths) is 0:
        print("Must pass token_to_nb files and at least one data file")
        sys.exit(1)
    x_length = kept_main_tokens + 1
    y_length = nb_tokens_in_context * (kept_context_tokens + 1)
    total_examples = count_samples(data_paths)
    total_samples = total_examples * sampling_rate
    
    print("Total samples: " + str(total_examples))
    print("Will sample about " + str(total_samples))
    
    model = Sequential()
    model.add(Dense(200, input_shape=(x_length,), name="hidden"))
    model.add(Dense(y_length, activation="sigmoid"))
    
    # using sigmoid for last layer + binary crossentropy because commonly used for multi-label, multi-class classification
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
#     model.compile(loss=weighted_loss, optimizer='adam', metrics=[weighted_accuracy])
    
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
        
    
    
    
    