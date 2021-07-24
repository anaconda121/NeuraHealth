# %run load_data/load_data.py

# import libraries
import csv, os
import json
from pathlib import Path
import django.shortcuts
from gui.models import Sentence, SeedRegex, PatientDemographic, Note
import sys

csv.field_size_limit(1000000000)

# everything is relative to this file
ROOT_DIR = Path(__file__).parent

# specify the import filename
filename = "char_limit.csv"

columns = [
    "PatientID",
    "MRN",
    "EMPI",
    "PatientEncounterID", 
    "NoteType",
    "NoteID",
    "Sentence",
    "RegexMatches"
]
column_overrides = {
    "Sentence": "regex_sent",
    "RegexMatches": "regex_match"
}
column_mapping = {
    c: column_overrides.get(c, c) for c in columns
}

print("CM: ", column_mapping)

patients = {}
notes = {}
regexes = {}
# read file and create patients, notes and seed regexes
with open(ROOT_DIR / filename, "r", encoding = 'utf-8') as f:
    rows = csv.DictReader(f)
    patient_ids = set() # (patient_id, mrn, empi)
    note_ids = set() # (patient_id, note_id, encounter_id)
    all_regexes = set()
    for row in rows:
        pid = row[column_mapping["PatientID"]]
        mrn = row[column_mapping["MRN"]]
        empi = row[column_mapping["EMPI"]]
        patient_ids.add((pid, mrn, empi))
        nid = row[column_mapping["NoteID"]]
        eid = row[column_mapping["PatientEncounterID"]]
        note_ids.add((pid, nid, eid))
        regex_match = row[column_mapping['RegexMatches']]
        try:
            regexes = json.loads(regex_match)
            for regex in regexes:
                all_regexes.add(regex)
        except:
            pass
    for patient_id, mrn, empi in patient_ids:
        p = PatientDemographic(PatientID=patient_id, MRN=mrn, EMPI=empi).save()
        patients[patient_id] = p
    #print("NoteIDS: ", note_ids)
    for patient_id, note_id, encounter_id in note_ids:
        print("PI: ", patient_id, "NI: ", note_id, "EI: ", encounter_id, "Date: ", Note(PatientID=patient_id, PatientEncounterID=encounter_id, NoteID=note_id).Date)
        n = Note(PatientID=patient_id, PatientEncounterID=encounter_id, NoteID=note_id).save()
        notes[note_id] = n
    for regex in all_regexes:
        r = SeedRegex(Pattern=regex).save()
        regexes[regex] = r

# start
with open(ROOT_DIR / filename, "r", encoding = 'utf-8') as f:
    rows = csv.DictReader(f)
    sentences = []
    for row in rows:
        sentence = row[column_mapping['Sentence']]
        sentence = json.loads(sentence)
        r = row[column_mapping['RegexMatches']]
        nid = row[column_mapping["NoteID"]]
        note = notes[nid]
        s = Sentence(Contents=sentence, Note=note).save()
        sentences.append(s)

print(f"Inserted {len(sentences)} sentences for {len(notes)} notes from {len(patients)} patients")
