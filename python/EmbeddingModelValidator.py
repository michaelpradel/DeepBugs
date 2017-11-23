'''
Created on Jul 17, 2017

@author: Michael Pradel
'''

import sys
from os import getcwd
from os.path import join
import json
from keras.models import load_model
import numpy as np
from keras import backend as K
import random
from numpy import float32

nb_tokens_in_context = 20
kept_main_tokens = 10000
kept_context_tokens = 1000

# custom loss and accuracy to account for unbalanced y vectors          
weight_of_ones = kept_context_tokens

def weighted_loss(y_true, y_pred):
    weights = y_true * weight_of_ones
    clipped_y_pred = K.clip(y_pred, K.epsilon(), None)
    weighted_cross_entropy = -(y_true * K.log(clipped_y_pred) * weights)
    result = K.mean(weighted_cross_entropy)
    return result
    
def weighted_accuracy(y_true, y_pred):
    weights = y_true * weight_of_ones
    weighted_equal = K.cast(K.equal(y_true, K.round(y_pred)), K.floatx()) * weights
    return K.mean(weighted_equal)

def get_xy_pair(path):
    encoded_tokens_with_context = np.load(path)
    for token_with_context in encoded_tokens_with_context:
        sample = random.random() < 0.001
        if sample:
            # encode token and context as one-hot vectors 
            # first element of token_with_context = number of main token
            x = np.zeros(kept_main_tokens + 1)
            x[token_with_context[0]] = 1
            
            y = np.zeros(nb_tokens_in_context * (kept_context_tokens + 1))
            for idx, nb_of_context_token in enumerate(token_with_context[1:]): # 2nd, 3rd, etc. element of token_with_context = numbers of context tokens
                offset = idx * (kept_context_tokens + 1)
                y[offset + nb_of_context_token] = 1
            
            yield (x, y)

if __name__ == '__main__':
    # arguments: <stored_model_file> <encoded_tokens_with_context_file>
    if len(sys.argv) < 3:
        print("Insufficient arguments")
        sys.exit(10)
    model_file = sys.argv[1]
    token_with_context_file = sys.argv[2]
    
    model = load_model(model_file, custom_objects={"weighted_loss":weighted_loss, "weighted_accuracy":weighted_accuracy})
    
    nb_examples = 0
    for (x, y_true) in get_xy_pair(token_with_context_file):
        print("x: "+str(x))
        xs = np.asarray([x])
        ys = model.predict(xs)
        y_pred = ys[0]
        print("y_pred: "+str(y_pred))
        y_rounded = K.eval(K.round(y_pred))
        print("y_rounded: "+str(y_rounded))
        y_true = y_true.astype(float32)
        print("y_true   : "+str(y_true))
        print("accuracy : "+str(K.eval(weighted_accuracy(y_true, y_pred))))
        
        nb_examples += 1
        if nb_examples > 0:
            break
    
    
    