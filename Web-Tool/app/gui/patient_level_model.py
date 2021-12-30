# Author: Tanish Tyagi 

# base libraries
import numpy as np
import pandas as pd
import regex as re
import itertools
import sklearn.metrics as sk
from functools import reduce
import pickle

def feature_engineering(notes):
    data = []
    seq_count = len(notes)

    if (seq_count <= 11):
        seq_count = 0
    elif (seq_count <= 23):
        seq_count = 1
    elif (seq_count <= 45):
        seq_count =2
    else:
        seq_count = 3

    p_yes = len(notes[notes["pred"] == 2]) / len(notes)
    p_no = len(notes[notes["pred"] == 0]) / len(notes)
    p_ntr = len(notes[notes["pred"] == 1]) / len(notes)

    curr_dict = {
        "percent_yes" : p_yes,
        "percent_no" : p_no,
        "percent_neither" : p_ntr,
        "sequence_count" : seq_count,
    }

    data.append(curr_dict)

    patient_level_features = pd.DataFrame(data)

    return patient_level_features

def run_patient_level(notes):
    patient_level_features = feature_engineering(notes)
    
    model = pickle.load(open("static/lr_12_26_patient_level.sav", "rb"))

    pred = model.predict(patient_level_features)
    proba = model.predict_proba(patient_level_features)

    patient_level_features["pred"] = pred
    patient_level_features["proba"] = str(proba)

    return patient_level_features