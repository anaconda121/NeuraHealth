# import libraries
import csv, os
from datetime import datetime
import json
from pathlib import Path
import openpyxl
import django.shortcuts
import logging
from gui.models import Sentence, SeedRegex, PatientDemographic, Note, SentenceSeedRegex
from django.db import transaction


logging.basicConfig(level="INFO", format='%(asctime)s %(levelname)-8s %(message)s')
logger = logging.getLogger("load_data")

@transaction.atomic
def load_data(filename, start_row=1):
    # everything is relative to this file
    # ROOT_DIR = Path(__file__).parent

    # specify the import filename
    # filename = "test_data.csv"
    fpath = filename

    columns = [
        "PatientID",
        "MRN",
        "EMPI",
        "PatientEncounterID", 
        "NoteType",
        "NoteID",
        "Sentence",
        "RegexMatches",
        "Date"
    ]
    column_overrides = {
        "Sentence": "regex_sent",
        "RegexMatches": "regex_match",
        "Date": "ContactDTS",
    }
    column_mapping = {
        c: column_overrides.get(c, c) for c in columns
    }

    date_fmt = "%Y-%m-%d"

    patients = {}
    notes = {}
    regexes = {}
    sentences = []

    def get_or_create_patient(patient_id, mrn, empi):
        existing = patients.get(patient_id)
        if existing:
            return existing
        p, created = PatientDemographic.objects.get_or_create(PatientID=patient_id, MRN=mrn, EMPI=empi)
        p.save()
        if created:
            patients[patient_id] = p
        return p

    def get_or_create_note(patient_id, note_id, encounter_id, date):
        existing = notes.get(note_id)
        if existing:
            return existing
        n, created = Note.objects.get_or_create(PatientID=patient_id, PatientEncounterID=encounter_id, NoteID=note_id, Date=date)
        n.save()
        if created:
            notes[note_id] = n
        return n

    def get_or_create_seed_regex(pattern):
        pattern = pattern.strip()
        existing = regexes.get(pattern)
        if existing:
            return existing
        r, created = SeedRegex.objects.get_or_create(Pattern=pattern)
        r.save()
        if created:
            regexes[pattern] = r
        return r

    with open(fpath, "r", encoding='utf-8-sig') as f:
        rows = csv.DictReader(f)    
        for row_num, row in enumerate(rows, 1):
            try:
                if row_num < start_row:
                    continue
                logger.debug(f"parsing row {start_row}")
                pid = row[column_mapping["PatientID"]]
                mrn = row[column_mapping["MRN"]]
                empi = row[column_mapping["EMPI"]]
                patient = get_or_create_patient(pid, mrn, empi)

                nid = row[column_mapping["NoteID"]]
                eid = row[column_mapping["PatientEncounterID"]]
                date = row[column_mapping["Date"]]
                date = datetime.strptime(date, date_fmt)
                note = get_or_create_note(pid, nid, eid, date)
                
                logger.debug(f"creating sentence for row {start_row}")
                sentence = row[column_mapping['Sentence']]
                sentence = json.loads(sentence)
                s = Sentence(Contents=sentence, Note=note)
                s.save()
                sentences.append(s)

                logger.debug(f"parsing regex from row {start_row}")
                regex_match = row[column_mapping['RegexMatches']]
                try:
                    matches = json.loads(regex_match)
                    logger.debug(f"creating regexes from row {start_row}")
                    for regex in matches:
                        seed_regex = get_or_create_seed_regex(regex)
                        assoc = SentenceSeedRegex(Sentence=s, SeedRegex=seed_regex)
                        assoc.save()
                except Exception as e:
                    logger.exception(f"Failed parsing regexes! Skipping row {row_num}")
            except:
                logger.exception(f"Failed on row {row_num}. Please check the data and restart the import.")
                raise    
            logger.info(f"Inserted sentence {row_num}")

    logger.info(f"Inserted {len(sentences)} sentences for {len(notes)} notes from {len(patients)} patients")
    logger.info(f"Database now has {Sentence.objects.count()} sentences for {Note.objects.count()} notes and {PatientDemographic.objects.count()} patients")
    