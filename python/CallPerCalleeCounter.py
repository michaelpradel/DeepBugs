'''
Created on Nov 7, 2017

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
    callee_to_calls = Counter();
    for call in Util.DataReader(call_data_paths):
        callee = call["callee"]
        callee_to_calls[callee] += 1

    time_stamp = math.floor(time.time() * 1000)
    callee_to_calls_file = "callee_to_calls_" + str(time_stamp) + ".json"
    with open(callee_to_calls_file, "w") as file:
        json.dump(callee_to_calls, file, sort_keys=True, indent=4)
        
    
    
    