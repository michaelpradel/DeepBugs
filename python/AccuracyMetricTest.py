'''
Created on Jul 17, 2017

@author: Michael Pradel
'''


from keras import backend as K
import numpy as np

nb_tokens_in_context = 2
kept_context_tokens = 5
weight_of_ones = kept_context_tokens

def weighted_loss(y_true, y_pred):
    weights = (y_true * (weight_of_ones - 1) + 1)
    y_pred = K.variable(y_pred) ## required only for debugging (if arguments come from backend, no need to convert them) 
    clipped_y_pred = K.clip(y_pred, K.epsilon(), None)
    weighted_cross_entropy = -(y_true * K.log(clipped_y_pred) * weights)
    result = K.mean(weighted_cross_entropy)
    assert not np.isnan(K.eval(result))
    return result
    
def weighted_accuracy(y_true, y_pred):
    weights = (y_true * (weight_of_ones - 1) + 1)
    equal = K.cast(K.equal(y_true, K.round(y_pred)), K.floatx())
    debug = K.eval(equal)
    weighted_equal = equal * weights
    return K.mean(weighted_equal)

if __name__ == '__main__':
    y_true = np.zeros(nb_tokens_in_context * kept_context_tokens)
    y_true[2] = 1
    y_true[7] = 1
    y_pred = np.ones(nb_tokens_in_context * kept_context_tokens)
#     y_pred[2] = 0.1
#     y_pred[7] = 0.99
    
    print("Accuracy: " + str(K.eval(weighted_accuracy(y_true, y_pred))))
    print("Loss: " + str(K.eval(weighted_loss(y_true, y_pred))))