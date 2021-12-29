# Author: Tanish Tyagi 

# base libraries
import numpy as np
import pandas as pd
import regex as re
import itertools
import sklearn.metrics as sk
from functools import reduce

# deep learning libraries
import torch
import transformers
from sklearn.model_selection import train_test_split
from simpletransformers.classification import ClassificationModel, ClassificationArgs


# file system manipulation
import os
import shutil
from pathlib import Path
import pickle
import copy

cuda_available = torch.cuda.is_available()
print("Is CUDA available? ", "Yes" if cuda_available else "No")


path = r"C:\Users\tanis\OneDrive - Phillips Exeter Academy\Data\Programming\APOE-SLAT\Models\Bert\best_model\trial_0"

best_model = ClassificationModel(
    "bert",
    path, 
    use_cuda=False,  
)


def run_cb(notes):
    """
    notes: dataframe generated from sequence_extraction_pipeline.py 
    """
    # print("cb: ", __name__, type(__name__))

    if __name__ == 'run_clinical_bert':
        # print("running")
        # notes = notes["text"]
        preds, outputs = best_model.predict(
            notes["text"].to_list()
        )

        # print("test2")

        max_prob_list = []
        test_prob_list = []
        test_pred_list = []
        for i in range(len(notes)):
            # prob_list = list(torch.softmax(torch.from_numpy(model_outputs[i]), axis=0)[:,1])
            prob_list = torch.softmax(torch.from_numpy(outputs[i]), axis=0)
            #print("Prob List: ", prob_list, type(prob_list))

            extracted_prob_list = []
            for i in range(len(prob_list)):
                extracted_prob_list.append(float(prob_list[i]))

            #print("Extracted Prob List: ", extracted_prob_list)
            # find max one in each submatrix of length 3
            max_proba = max(extracted_prob_list)

            # identify model prediction based on location of max_proba within extracted_prob_list
            if (extracted_prob_list[0] == max_proba):
                test_pred_list.append(0)
            elif (extracted_prob_list[1] == max_proba):
                test_pred_list.append(1)
            else:
                test_pred_list.append(2)

            max_prob_list.append(max_proba)
            test_prob_list.append(extracted_prob_list)

        notes["pred"] = test_pred_list
        notes["proba"] = max_prob_list

    return notes 