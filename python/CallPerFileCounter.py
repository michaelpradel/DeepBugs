'''
Created on Nov 3, 2017

@author: Michael Pradel
'''

import json
import math
import sys
import time

import random

import Util
from collections import Counter

if __name__ == '__main__':
    # arguments: <call data files>
    
    call_data_paths = sys.argv[1:]
    file_name_to_calls = Counter();
    for call in Util.DataReader(call_data_paths):
        file_name = call["filename"]
        file_name_to_calls[file_name] += 1

    time_stamp = math.floor(time.time() * 1000)
    file_name_to_calls_file = "file_name_to_calls_" + str(time_stamp) + ".json"
    with open(file_name_to_calls_file, "w") as file:
        json.dump(file_name_to_calls, file, sort_keys=True, indent=4)
        
    
    
    