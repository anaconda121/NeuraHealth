# Author: Tanish Tyagi

from django.shortcuts import render

import pandas as pd

from sequence_extraction_pipeline import sequence_extraction_pipeline
from run_clinical_bert import run_cb
from patient_level_model import run_patient_level

def generate_output():
    """
    notes: dataframe with seq data and model preds
    """
    path = r"C:\Users\tanis\OneDrive - Phillips Exeter Academy\Data\Programming\APOE-SLAT\Web-Tool\app\gui\static\test_notes.txt"
    notes = sequence_extraction_pipeline(path)
    notes = notes.rename(columns = {'regex_sent': 'text'}) 
    notes = run_cb(notes)
    notes.to_csv(r"static/test_preds.csv", index = False)
    patient_level_features = run_patient_level(notes)
    patient_level_features.to_csv(r"static/patient_level_pred.csv", index = False)

generate_output()