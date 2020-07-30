# Readme 
# Testing Bug_Find
# with all programs listed in ./data/js/programs_50_all.txt
# the programs where found in ./data/js/programs_50
# 
# in the ./tests directory the following start scripts are located:
#
# start_BugFind.py
# 
#
# author: Sabine Zach, last changed on July, 22, 2020

# from the project's main directory you can
# start the Testing Routine with the following command

python3 ./tests/start_BugFind.py

# Prerequsites:

For each bug pattern:

 * please put the trained classifier in
   ./models/<bugpattern>/bug_detection_model
   e.g.
   ./models/SwappedArgs/bug_detection_model
   ./models/BinOperator/bug_detection_model
   ./models/SwappedBinOperands/bug_detection_model
   etc.

You'll find the results of prediction in the following files
  * predict_%time.txt    *%time ist the timestamp
  * there is one file per bug pattern
in the project's main directory.

Please use keras with tensorflow. For example, with the following installation:
  * tensorflow 2.2.0 
  * keras 2.4.3 

Edit the configuration file for keras.

Edit:
  * ~/.keras/keras.json
Set:
  * "backend": "tensorflow",

keras.json Example:
  {
      "floatx": "float32",
      "epsilon": 1e-07,
      "backend": "tensorflow",
      "image_data_format": "channels_last"
  }
