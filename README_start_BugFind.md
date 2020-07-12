# Readme 
# Testing Bug_Find
# with all programs listed in ./data/js/programs_50_all.txt
# the programs where found in ./data/js/programs_50
# sza, 20200711

# start the Testing Routine with the following command
python3 start_BugFind.py

# Prerequsites:

For each bug pattern:

 * please put the trained classifier in
   ./bugpattern/bug_detection_model
   e.g.
   ./SwappedArgs/bug_detection_model
   ./BinOperator/bug_detection_model
   ./SwappedBinOperands/bug_detection_model
   etc.

For the programs list:

  * please join ./data/js/programs_50_training.txt
     and        ./data/js/programs_50_eval.txt
    and save the result in
                ./data/js/programs_50_all.txt

You'll find the results of prediction in the following files:
  * predict_%time.txt    *%time ist the timestamp
  * there is one file per bug pattern
