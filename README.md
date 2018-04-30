DeepBugs: Deep Learning to Find Bugs
====================================

DeepBugs is a framework for learning name-based bug detectors from an existing code corpus. See [this technical report](http://mp.binaervarianz.de/DeepBugs_TR_Nov2017.pdf) for a detailed description.

Overview
-------------
* All commands are called from the main directory.
* Python code (most of the implementation) and JavaScript code (for extracting data from .js files) are in the `/python` and `/javascript` directories.
* All data to learn from, e.g., .js files are expected to be in the `/data` directory.
* All data that is generated, e.g., intermediate representations, are written into the main directory. It is recommended to move them into separate directories.
* All generated data files have a timestamp as part of the file name. Below, all files are used with `*`. When running commands multiple times, make sure to use the most recent files.


Requirements
------------------

* Node.js
* npm modules (install with `npm install module_name`): acorn, estraverse, walk-sync
* Python 3
* Python packages: keras, scipy, numpy, sklearn


JavaScript Corpus
-----------------------

* The full corpus can be downloaded [here](http://www.srl.inf.ethz.ch/js150.php) and is expected to be stored in `data/js/programs_all`. It consists of 100.000 training files, listed in `data/js/programs_training.txt`, and 50.000 files for validation, listed in `data/js/programs_eval.txt`. 
* This repository contains only a very small subset of the corpus. It is stored in `data/js/programs_50`. Training and validation files for the small corpus are listed in `data/js/programs_50_training.txt` and `data/js/programs_50_eval.txt`.


Learning a Bug Detector
-------------------------------

Creating a bug detector consists of two main steps:
1) Extract positive (i.e., likely correct) and negative (i.e., likely buggy) training examples from code.
2) Train a classifier to distinguish correct from incorrect code examples.

Each bug detector addresses a particular bug pattern, e.g.:

  * The `SwappedArgs` bug detector looks for accidentally swapped arguments of a function call, e.g., calling `setPoint(y,x)` instead of `setPoint(x,y)`.
  * The `BinOperator` bug detector looks for incorrect operators in binary operations, e.g., `i <= len` instead of `i < len`.
  * The `IncorrectBinaryOperand` bug detector looks for incorrect operands in binary operations, e.g., `height - x` instead of `height - y`.

#### Step 1: Extract positive and negative training examples

`node javascript/extractFromJS.js calls --parallel 4 data/js/programs_50_training.txt data/js/programs_50`

  * The `--parallel` argument sets the number of processes to run.
  * `programs_50_training.txt` contains files to include (one file per line). To extract data for validation, run the command with `data/js/programs_50_eval.txt`.
  * The last argument is a directory that gets recursively scanned for .js files, considering only files listed in the file provided as the second argument.
  * The command produces `calls_*.json` files, which is data suitable for the `SwappedArgs` bug detector. For the other bug two detectors, replace `calls` with `binOps` in the above command.

#### Step 2: Train a classifier to identify bugs

`python3 python/AnomalyDetector2.py SwappedArgs --learn token_to_vector.json type_to_vector.json node_type_to_vector.json --trainingData calls_xx*.json --validationData calls_yy*.json`

  * The first argument selects the bug pattern.
  * The next three arguments are vector representations for tokens (here: identifiers and literals), for types, and for AST node types. These files are provided in the repository.
  * The remaining arguments are two lists of .json files. They contain the training and validation data extracted in Step 1.
  * After learning the bug detector, the command measures accurracy and recall w.r.t. seeded bugs and writes a list of potential bugs in the unmodified validation code (see `poss_anomalies.txt`).

Note that learning a bug detector from the very small corpus of 50 programs will yield a classifier with low accuracy that is unlikely to be useful. To leverage the full power of DeepBugs, you'll need a larger code corpus, e.g., the [JS150 corpus](http://www.srl.inf.ethz.ch/js150.php) mentioned above.


Embeddings for Identifiers
----------------------------------

The above bug detectors rely on a vector representation for identifier names and literals. To use our framework, the easiest is to use the shipped `token_to_vector.json` file. Alternatively, you can learn the embeddings via Word2Vec as follows:

1) Extract identifiers and tokens:

`node javascript/extractFromJS.js tokens --parallel 4 data/js/programs_50_training.txt data/js/programs_50`

  * The command produces `tokens_*.json` files.
  
2) Encode identifiers and literals with context into arrays of numbers (for faster reading during learning):
  
  `python3 python/TokensToTopTokens.py tokens_*.json`
  
  * The arguments are the just created files.
  * The command produces `encoded_tokens_*.json` files and a file `token_to_number_*.json` that assigns a number to each identifier and literal.

3) Learn embeddings for identifiers and literals:
  
  `python3 python/EmbeddingsLearnerWord2Vec.py token_to_number_*.json encoded_tokens_*.json`

  * The arguments are the just created files.
  * The command produces a file `token_to_vector_*.json`.
