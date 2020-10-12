#!/bin/bash

# set this to the directory the token embeddings are stored in
emb_dir="./data/embeddings/emb100"

# list different token embeddings to evaluate (assumes to find .json files in the above directory)
embeddings="FT_orig FT_counterfitted2"

# must be a directory you can write to
model_dir="./data/known_bugs/models"

patterns="SwappedArgs BinOperator IncorrectBinaryOperand IncorrectAssignment"

for pattern in ${patterns}
do
    for emb in ${embeddings}
    do
        # Learn model
        printf "\n@@@ Learning model for ${pattern} and ${emb} @@@\n\n"
        python python/BugLearn.py --pattern ${pattern} \
        --token_emb ${emb_dir}/${emb}.json \
        --type_emb type_to_vector.json --node_emb node_type_to_vector.json \
        --training_data data/${pattern}/training/*.json \
        --out ${model_dir}/bug_detection_model_${pattern}_${emb}
        
        # Find bugs using learned model
        printf "\n@@@ Trying to find known bugs for ${pattern} and ${emb}@@@\n\n"
        python python/BugFind.py --pattern ${pattern} \
        --token_emb ${emb_dir}/${emb}.json \
        --type_emb type_to_vector.json --node_emb node_type_to_vector.json \
        --testing_data data/known_bugs/js_data_relevant_${pattern}/*buggy.json \
        --model ${model_dir}/bug_detection_model_${pattern}_${emb} \
        --threshold 0.5
        &> known_bugs_buggy_${pattern}_${emb}.out

        python python/BugFind.py --pattern ${pattern} \
        --token_emb ${emb_dir}/${emb}.json \
        --type_emb type_to_vector.json --node_emb node_type_to_vector.json \
        --testing_data data/known_bugs/js_data_relevant_${pattern}/*fixed.json \
        --model ${model_dir}/bug_detection_model_${pattern}_${emb} \
        --threshold 0.5
        &> known_bugs_fixed_${pattern}_${emb}.out
    done
done
