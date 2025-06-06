#!/bin/bash
MODEL_NAME=$1
#MODEL_NAME='/home/chensh/hub/model/llama-2-7b-hf'
OUTPUT_PATH='outputs/wina/Llama-2-7B'
MODEL_TYPE=Llama-2-7B
SPARSE_MODE='wina'

# compute sparsity for each layer
python wina/grab_acts.py --model_name $MODEL_NAME --output_path $OUTPUT_PATH --sparse_mode $SPARSE_MODE --transform
python wina/greedyopt.py --model_name $MODEL_NAME --output_path $OUTPUT_PATH --sparse_mode $SPARSE_MODE --model_type $MODEL_TYPE --transform

# topk-based gate
mask_by='topk'
for sparsity in 0.25 0.4 0.5 0.65
do
    # lm-eval harness
    python eval.py --base_model $MODEL_NAME --save_path $OUTPUT_PATH --sparsity $sparsity --sparse_mode $SPARSE_MODE --mask_by $mask_by --greedy --transform
done