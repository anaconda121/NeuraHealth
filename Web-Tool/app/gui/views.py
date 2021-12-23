from django.shortcuts import render

import pandas as pd
import regex as re

regex = pd.read_csv(r"static/keywords.csv")

def compile_regex():
    # importing keywords and case
    k = regex["REGEX"].to_list()
    c = regex["CASE"].to_list()
    p_list = []

    # compiling regex
    for i in range(len(k)):
        if (c[i] == 1):
            p_list.append(re.compile(k[i]))
        else:
            p_list.append(re.compile(k[i], re.IGNORECASE))

    return p_list 

def read_notes(note_txt):
    # dataframe to save notes to 
    note_df = pd.DataFrame(columns = ["NoteTXT"])

    # opening file and extracting lines
    notes = open(note_txt, "r")
    lines = notes.readlines()
    note_list = []

    for line in lines:
        # print("line", line.strip())
        note_list.append(line.strip())

    note_df["NoteTXT"] = note_list
    
    return note_df 

def find_matches(notes, keywords):
    # array for storing keyword matches
    matches = [] 

    for note in notes["NoteTXT"]:
        curr = []

        # finding matches 
        for p in (keywords):
            m = list(set(re.findall(p, note)))
            m = list(set(map(str.lower, m)))
            if (m != []):
                curr.append("".join(m))

        matches.append(str(curr))

    return matches 

def sequence_extraction_pipeline(note_txt):
    """
    note_txt: file path (?) that contains all notes, notes are separated by a line
    """
    # TODO: clean up extraction pipeline from web form 
    notes = read_notes(note_txt)

    # creation of compiled keyword list
    keywords = compile_regex()

    # getting matches from notes
    matches = find_matches(notes, keywords)
    notes["regex_matches"] = matches  

    return notes 

def tester():
    notes = sequence_extraction_pipeline(r"C:\Users\tanis\OneDrive - Phillips Exeter Academy\Data\Programming\APOE-SLAT\Web-Tool\app\gui\static\test_notes.txt")
    print(notes["regex_matches"]) 

tester()