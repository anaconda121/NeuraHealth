# Author: Tanish Tyagi

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
    """
    note_txt: file path that contains notes
    """
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
    """
    notes: dataframe
    keywords: list of compiled regex expressions for 18 dementia-related keywords
    """
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

def find_character_locations(notes, keywords):
    """
    notes: dataframe 
    keywords: list of compiled regex expressions for 18 dementia-related keywords
    """
    # array for storing character locations of matches; list of tuples
    locations = []

    for r in (notes['NoteTXT']):
        curr_loc = []

        # finding character locations
        for p in keywords:
            for match in re.finditer(p ,r):
                curr_loc.append(match.span())
                
        # TODO: decide if need to keep this code
        # current logic; if no character location is found, something is wrong
        if (curr_loc == []):
            print("STOP")
            break
            
        locations.append(curr_loc)
    
    return locations 

# TODO: This function may not be needed if rows that have no keyword matches are kept 
def create_context_windows(notes, i):
    """
    notes: dataframe 
    i: int that represents index in notes
    """
    merged = []
    context_length_one_direction = 100
    
    for j in range(len(notes["regex_location"][i])):
        start = notes["regex_location"][i][j][0]
        end = notes["regex_location"][i][j][1]

        # creating context windows
        prune_start = False
        prune_end = False

        if (start - context_length_one_direction <= 0):
            start = 0
            prune_start = True
        if (end + context_length_one_direction >= len(notes["NoteTXT"][i]) - 1):
            end = len(notes["NoteTXT"][i]) - 1
            prune_end = True 

        if (prune_start and prune_end):
            merged.append((start, end))
        else:
            if (prune_start):
                merged.append((start, end + context_length_one_direction))
            if (prune_end):
                merged.append((start - context_length_one_direction, end))

        if (not prune_start and not prune_end):
            merged.append((start - context_length_one_direction, end + context_length_one_direction))
    
    return merged

def merge(intervals):  
    """
    intervals: list of tuples representing context windows 
    """
    ans = []
    i = 1
    intervals.sort()
    tempans = intervals[0]
    
    while i < len(intervals):
        # seeing if context windows overlap with each other - if they do merge them together
        if tempans[0] <= intervals[i][1] and tempans[1] >= intervals[i][0]:
            newtempans = [min(tempans[0] , intervals[i][0]) , max(tempans[1] , intervals[i][1])]
            tempans = newtempans
            i += 1
        else:
            ans.append(tempans)
            tempans = intervals[i]
            i += 1
            
    ans.append(tempans)
    return ans

def sequence_extraction_pipeline(note_txt):
    """
    note_txt: file path (TODO: decide this?) that contains all notes, notes are separated by a line
    """
    # TODO: clean up extraction pipeline from web form 
    notes = read_notes(note_txt)

    # creation of compiled keyword list
    keywords = compile_regex()

    # getting matches from notes
    matches = find_matches(notes, keywords)
    notes["regex_matches"] = matches  

    # TODO: decide if drop rows that do not have regex match -- I think no?

    # getting character locations for notes
    character_locations = find_character_locations(notes, keywords)
    notes["regex_location"] = character_locations 

    # creating context windows
    context_windows = []
    for i in range(len(notes)):
        context_windows.append(create_context_windows(notes, i))
    notes["context_windows"] = context_windows

    # merging context windows on note level
    merged = []
    for i in range(len(notes)):
        merged.append(merge(notes["context_windows"][i]))
    notes["merged_row_location"] = merged 

    return notes 

def tester():
    notes = sequence_extraction_pipeline(r"C:\Users\tanis\OneDrive - Phillips Exeter Academy\Data\Programming\APOE-SLAT\Web-Tool\app\gui\static\test_notes.txt")
    print(notes["merged_row_location"]) 

tester()