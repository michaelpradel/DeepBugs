'''
Created on July 07, 2020

@author: Sabine Zach

Last Changed on July 25, 2020

@by: Sabine Zach
'''
# Skript for Testing Bug_Find
# Tests for all bug patterns
#
# called by: $python3 ./tests/start_BugFind.py
#
# Prerequisites:
# Data: data/js/programs_50
#       data/js/programs_all.txt
# Models for all patterns: models/what/bug_detection_model
# what stands for
#      SwappedArgs
#      BinOperator
#      SwappedBinOperands
#      IncorrectBinaryOperand
#
# on line 147 you can set a threshold for the prediction output

import sys
import json
import math
import time
from os import getcwd
from os import remove
from os.path import exists
from shutil import copyfile

from subprocess import call, check_output

##--------------------------------------------------------
def get_all_js_files(txt_file):
    ##--------get input data file names out of text file----
    all_js_files = ''
    p50 = open(txt_file, 'r+')
    for js_name in p50:
        all_js_files = all_js_files + ' ' + js_name.replace('\n','')
    return all_js_files
##--get all js file names---------------------------------

##--------------------------------------------------------
def what_to_bugspec(what):
    bugspec = "calls"             #not entirely accurate
    if what == "SwappedArgs":
        bugspec = "calls"
    elif what == "BinOperator":
        bugspec = "binOps"
    elif what == "IncorrectBinaryOperand":
        bugspec = "binOps"
    elif what == "SwappedBinOperands":
        bugspec = "binOps"
    #--todo
    #elif what == "MissingArg":
    #    bugspec = "????"
    #elif what == "IncorrectAssignment":
    #    bugspec = "????"
    else:
        pass
    return bugspec
##--change 'what' to 'bugspec'----------------------------

##--------------------------------------------------------
def extract_from_js(bugspec, all_js_data_files):
    ##----------------------------------------------------
    ##  produces calls_xx*.json
    ##       or  binOps_xx*.json files
    ##  see javascript/extractFromJS.js
    ##----------------------------------------------------

    ##----create outfile name----
    time_stamp = math.floor(time.time() * 1000)
    outfile_json = bugspec + '_' + str(time_stamp) + ".json"
    outfile_str = '--outfile ' + outfile_json

    ##extract command
    data_extract_str = 'node ./javascript/extractFromJS.js ' + bugspec + ' --files '

    ##execute extract command
    print( '%s %s %s' %(data_extract_str, all_js_data_files, outfile_str))
    returned = call( '%s %s %s' %(data_extract_str, all_js_data_files, outfile_str), shell=True)
    if (returned != 0):
        print('extractFromJS returned: %d' %(returned))
        exit(1)

    print('extractFromJS has returned with %d' %(returned))
    print('Created file **%s**' % (outfile_json))

    ##--todo--in case > 1 outfile:
    ##return a string of all outfiles, separated by ' '
    data_json = outfile_json
    return data_json
##------extract_from_js ------------------------------------

##--------------------------------------------------------
if __name__ == '__main__':
    # arguments for start_BugFind: what
    #  what is one of: SwappedArgs
    #                  BinOperator
    #                  SwappedBinOperands
    #                  IncorrectBinaryOperand
    #                  IncorrectAssignment
    #                  MissingArg
    #                  IncorrectAssignment
    #

    print("**start BugFind.py for all bug patterns**\n\n ")

    ## use all bug patterns
    bugpatterns = ("SwappedArgs", "BinOperator", "SwappedBinOperands", "IncorrectBinaryOperand")

    for what in bugpatterns:
        ##------------change 'what' to 'bugspec'----
        ##  e.g.             'SwappedArgs' to 'calls'
        bugspec = what_to_bugspec(what)
        print("**" + what + "**\n")

        ##############################################
        ## call extract_from_js for data/js/programs50
        ##############################################

        ##-----get input data file names and extract code pieces-----
        js_txt_file = 'data/js/programs_50_all.txt'
        all_js_files = get_all_js_files(js_txt_file)
        str_of_json_files = extract_from_js(bugspec, all_js_files)

        ##the command produces calls_*.json files, or binOps*.json files, etc.
        ##depending on bugspec

        #######################
        ## end  extract_from_js
        #######################

        ## create arguments for BugFind:
        ##     <what> <p_threshold> --load <model file> <name to vector file> <type to vector file> <AST node type to vector file> --newData <list of data files in json format>
        ## e.g.
        ## SwappedArgs 0.02 --load ./models/SwappedArgs/bug_detection_model ./token_to_vector.json ./type_to_vector.json ./node_type_to_vector.json --newData "./calls_1.json ./calls_2.json ./calls_3.json"

        #####################
        ## call BugFind
        #####################
        what
        p_threshold = " 0.02"    #e.g.
        load = " --load"
        model_file = " ./models/" + what + "/bug_detection_model"
        token_to_vector_file = " ./token_to_vector.json"
        type_to_vector_file = " ./type_to_vector.json"
        node_type_to_vector_file = " ./node_type_to_vector.json"
        new = " --newData"
        json_files = ' ' + str_of_json_files

        ##construct command for calling
        call_bugfind_str = 'python3 ./python/BugFind.py ' + what + p_threshold + load + model_file + token_to_vector_file + type_to_vector_file + node_type_to_vector_file + new + json_files
        print("calling BugFind:\n%s" %(call_bugfind_str))

        ##execute command
        ##--todo--  outfile_str
        ##--returned = call( '%s %s' %(newdata_extract_str, outfile_str), shell=True)

        returned = call( '%s' %(call_bugfind_str), shell=True)
        ##check the unix exit code
        if (returned != 0):
            print('can not call BugFind.py, returned: %d' %(returned))
            exit(2)
        print('BugFind.py called successfully: %d' %(returned))

        #####################
        ## end  BugFind
        #####################
    
        ## delete generated files #list_of_json_files
        ##    ===>   delete after running BugFind.py!!!!!!!
        print("delete ...................................\n")
        list_of_json_files = str_of_json_files.split()
        for json_file in list_of_json_files:
            print("json_file ... : %s" %(json_file))
            json_path = getcwd() + '/' + json_file
            if exists(json_path):
                remove(json_path)
        ids_json_file = "fileIDs.json"
        ids_json_path = getcwd() + '/' + ids_json_file
        if exists(ids_json_path):
            remove (ids_json_path)

        ## save prediction file produced by BugFind
        ## what - SwappedArgs, BinOperator, SwappedBinOperands, etc.
        prediction_name = "predictions"
        prediction_file = prediction_name + ".txt"
        prediction_path = getcwd() + '/' + prediction_file
        if exists(prediction_path):
            print(prediction_path + " exists.\n")
            ##----create outfile name----
            time_stamp = math.floor(time.time() * 1000)
            predict_t = prediction_name + '_' + str(time_stamp) + ".txt"
            predict_t_path = getcwd() + '/' + predict_t
            ## file copy !!!!
            copyfile(prediction_path, predict_t_path)
            remove (prediction_path)
    ##--end------------------for what in bugPatterns##
