'''
Created on Jun 23, 2017

@author: Michael Pradel
'''

import sys
import json
from os.path import join
from os import getcwd
from collections import Counter, namedtuple
import math
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Dropout
import random
import time
import Util
import LearningDataSwappedArgs
import LearningDataBinOperator
import LearningDataSwappedBinOperands
import LearningDataIncorrectBinaryOperand
import LearningDataIncorrectAssignment
import LearningDataMissingArg

name_embedding_size = 200
file_name_embedding_size = 50
type_embedding_size = 5

Anomaly = namedtuple("Anomaly", ["message", "score"])

def parse_data_paths(args):
    training_data_paths = []
    eval_data_paths = []
    mode = None
    for arg in args:
        if arg == "--trainingData":
            assert mode == None
            mode = "trainingData"
        elif arg == "--validationData":
            assert mode == "trainingData"
            mode = "validationData"
        else:
            path = join(getcwd(), arg)
            if mode == "trainingData":
                training_data_paths.append(path)
            elif mode == "validationData":
                eval_data_paths.append(path)
            else:
                print("Incorrect arguments")
                sys.exit(0)
    return [training_data_paths, eval_data_paths]

def prepare_xy_pairs(data_paths, learning_data):
    xs = []
    ys = []
    code_pieces = [] # keep calls in addition to encoding as x,y pairs (to report detected anomalies)
    
    for code_piece in Util.DataReader(data_paths):
        learning_data.code_to_xy_pairs(code_piece, xs, ys, name_to_vector, type_to_vector, node_type_to_vector, code_pieces)
    x_length = len(xs[0])
    
#     print("Stats: " + str(learning_data.stats))
    print("Number of x,y pairs: " + str(len(xs)))
    print("Length of x vectors: " + str(x_length))
    return [xs, ys, code_pieces]

if __name__ == '__main__':
    # arguments (for learning new model): what --learn <name to vector file> <type to vector file> <AST node type to vector file> --trainingData <list of call data files> --validationData <list of call data files>
    # arguments (for learning new model): what --load <model file> <name to vector file> <type to vector file> <AST node type to vector file> --trainingData <list of call data files> --validationData <list of call data files>
    #   what is one of: SwappedArgs, BinOperator, SwappedBinOperands, IncorrectBinaryOperand, IncorrectAssignment
    print("AnomalyDetector2 started with " + str(sys.argv))
    time_start = time.time()
    what = sys.argv[1]
    option = sys.argv[2]
    if option == "--learn":
        name_to_vector_file = join(getcwd(), sys.argv[3])
        type_to_vector_file = join(getcwd(), sys.argv[4])
        node_type_to_vector_file = join(getcwd(), sys.argv[5])
        training_data_paths, validation_data_paths = parse_data_paths(sys.argv[6:])
    elif option == "--load":
        print("--load option is buggy and currently disabled")
        sys.exit(1)
        model_file = sys.argv[3]
        name_to_vector_file = join(getcwd(), sys.argv[4])
        type_to_vector_file = join(getcwd(), sys.argv[5])
        node_type_to_vector_file = join(getcwd(), sys.argv[6])
        training_data_paths, validation_data_paths = parse_data_paths(sys.argv[7:])
    else:
        print("Incorrect arguments")
        sys.exit(1)
    
    with open(name_to_vector_file) as f:
        name_to_vector = json.load(f)
    with open(type_to_vector_file) as f:
        type_to_vector = json.load(f)
    with open(node_type_to_vector_file) as f:
        node_type_to_vector = json.load(f)
    
    if what == "SwappedArgs":
        learning_data = LearningDataSwappedArgs.LearningData()
    elif what == "BinOperator":
        learning_data = LearningDataBinOperator.LearningData()
    elif what == "SwappedBinOperands":
        learning_data = LearningDataSwappedBinOperands.LearningData()
    elif what == "IncorrectBinaryOperand":
        learning_data = LearningDataIncorrectBinaryOperand.LearningData()
    elif what == "IncorrectAssignment":
        learning_data = LearningDataIncorrectAssignment.LearningData()
    elif what == "MissingArg":
        learning_data = LearningDataMissingArg.LearningData()
    else:
        print("Incorrect argument for 'what'")
        sys.exit(1)
    
    print("Statistics on training data:")
    learning_data.pre_scan(training_data_paths, validation_data_paths)
    
    # prepare x,y pairs for learning and validation
    print("Preparing xy pairs for training data:")
    xs_training, ys_training, _ = prepare_xy_pairs(training_data_paths, learning_data)
    x_length = len(xs_training[0])
    print("Training examples   : " + str(len(xs_training)))
    
    # manual validation of stored model (for debugging)
    if option == "--load":
        model = load_model(model_file)
        print("Loaded model.")
    elif option == "--learn": 
        # simple feedforward network
        model = Sequential()
        model.add(Dropout(0.2, input_shape=(x_length,)))
        model.add(Dense(200, input_dim=x_length, activation="relu", kernel_initializer='normal'))
        model.add(Dropout(0.2))
        #model.add(Dense(200, activation="relu"))
        model.add(Dense(1, activation="sigmoid", kernel_initializer='normal'))
     
        # train
        model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        history = model.fit(xs_training, ys_training, batch_size=100, epochs=10, verbose=1)
        
        time_stamp = math.floor(time.time() * 1000)
        model.save("anomaly_detection_model_"+str(time_stamp))
    
    time_learning_done = time.time()
    print("Time for learning (seconds): " + str(round(time_learning_done - time_start)))
    
    print("Preparing xy pairs for validation data:")
    xs_validation, ys_validation, code_pieces_validation = prepare_xy_pairs(validation_data_paths, learning_data)
    print("Validation examples : " + str(len(xs_validation)))
    
    # validate
    validation_loss = model.evaluate(xs_validation, ys_validation)
    print()
    print("Validation loss & accuracy: " + str(validation_loss))
    
    # compute precision and recall with different thresholds for reporting anomalies
    # assumption: correct and swapped arguments are alternating in list of x-y pairs
    threshold_to_correct = Counter()
    threshold_to_incorrect = Counter()
    threshold_to_found_seeded_bugs = Counter()
    threshold_to_warnings_in_orig_code = Counter()
    ys_prediction = model.predict(xs_validation)
    poss_anomalies = []
    for idx in range(0, len(xs_validation), 2):
        y_prediction_orig = ys_prediction[idx][0] # probab(original code should be changed), expect 0
        y_prediction_changed = ys_prediction[idx + 1][0] # probab(changed code should be changed), expect 1
        anomaly_score = learning_data.anomaly_score(y_prediction_orig, y_prediction_changed) # higher means more likely to be anomaly in current code
        normal_score = learning_data.normal_score(y_prediction_orig, y_prediction_changed) # higher means more likely to be correct in current code
        is_anomaly = False
        for threshold_raw in range(1, 20, 1):
            threshold = threshold_raw / 20.0
            suggests_change_of_orig = anomaly_score >= threshold
            suggests_change_of_changed = normal_score >= threshold
            # counts for positive example
            if suggests_change_of_orig:
                threshold_to_incorrect[threshold] += 1
                threshold_to_warnings_in_orig_code[threshold] += 1
            else:
                threshold_to_correct[threshold] += 1
            # counts for negative example
            if suggests_change_of_changed:
                threshold_to_correct[threshold] += 1
                threshold_to_found_seeded_bugs[threshold] += 1
            else:
                threshold_to_incorrect[threshold] += 1
            
            # check if we found an anomaly in the original code
            if suggests_change_of_orig:
                is_anomaly = True
                
        if is_anomaly:
            code_piece = code_pieces_validation[idx]
            message = "Score : " + str(anomaly_score) + " | " + code_piece.to_message()
#             print("Possible anomaly: "+message)
            # Log the possible anomaly for future manual inspection
            poss_anomalies.append(Anomaly(message, anomaly_score))
    
    f_inspect = open('poss_anomalies.txt', 'w+')
    poss_anomalies = sorted(poss_anomalies, key=lambda a: -a.score)
    for anomaly in poss_anomalies:
        f_inspect.write(anomaly.message + "\n")
    print("Possible Anomalies written to file : poss_anomalies.txt")
    f_inspect.close()

    time_prediction_done = time.time()
    print("Time for prediction (seconds): " + str(round(time_prediction_done - time_learning_done)))
    
    print()
    for threshold_raw in range(1, 20, 1):
        threshold = threshold_raw / 20.0
        recall = (threshold_to_found_seeded_bugs[threshold] * 1.0) / (len(xs_validation) / 2)
        precision = 1 - ((threshold_to_warnings_in_orig_code[threshold] * 1.0) / (len(xs_validation) / 2))
        if threshold_to_correct[threshold] + threshold_to_incorrect[threshold] > 0:
            accuracy = threshold_to_correct[threshold] * 1.0 / (threshold_to_correct[threshold] + threshold_to_incorrect[threshold])
        else:
            accuracy = 0.0
        print("Threshold: " + str(threshold) + "   Accuracy: " + str(round(accuracy, 4)) + "   Recall: " + str(round(recall, 4))+ "   Precision: " + str(round(precision, 4))+"  #Warnings: "+str(threshold_to_warnings_in_orig_code[threshold]))
    
    
    