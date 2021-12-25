# Author: Tanish Tyagi

import pandas as pd
import regex as re
import warnings
warnings.filterwarnings("ignore")

from transformers import AutoTokenizer

# constants
tokenizer = AutoTokenizer.from_pretrained("emilyalsentzer/Bio_ClinicalBERT")
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

# TODO: will not be needed for notes that don't have keyword matches 
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

# TODO: will not be needed for notes that don't have keyword matches 
def pull_context_windows(notes, i, col):
    """
    notes: dataframe 
    i: int that represents index in notes
    col: name of column that has merged context windows 
    """
    # string that holds text for pulled context windows
    sequence = ""
    
    for j in range(len(notes[col][i])):
        # if multiple context windows per note
        if j > 0 and sequence != "":
            sequence += " ----- "
            
        start = notes[col][i][j][0]
        end = notes[col][i][j][1]
        
        sequence += notes["NoteTXT"][i][start : end]
    
    return sequence

def clinical_bert_tokenize(notes, i, col):
    """
    notes: dataframe 
    i: int that represents index in notes
    col: name of column that has merged context windows 
    """
    tokens = tokenizer.encode_plus(notes[col][i], add_special_tokens = False, return_tensors = 'pt')

    return (len(tokens['input_ids'][0]))

def generate_padded_context_windows(notes, i):
    """
    notes: dataframe 
    i: int that represents index in notes
    """    
    if (notes["token_length"][i] <= 400):
        locs = list((notes["merged_row_location"][i]))
        length = len(locs)
        start = locs[0][0] 
        end = locs[length - 1][1]
        
        #print(start, end)
                
        seq_length = 1000
        length_to_add_one_side = int((seq_length - notes["sequence_length"][i]) / 2)
        
        #print(length_to_add_one_side, notes["sequence_length"][i])
        
        prune_start = False
        prune_end = False
        if (start - length_to_add_one_side <= 0):
            start = 0
            prune_start = True
        if (end + length_to_add_one_side >= len(notes["NoteTXT"][i]) - 1):
            end = len(notes["NoteTXT"][i]) - 1
            prune_end = True
            
        # print(start, end, prune_start, prune_end)
        if(prune_start and prune_end):
            start = 0
            end = len(notes["NoteTXT"][i]) - 1
        elif (prune_start):
            end += length_to_add_one_side
            if (end + length_to_add_one_side <= len(notes["NoteTXT"])):
                end += length_to_add_one_side
        elif (prune_end):
            start -= length_to_add_one_side
            if (start - length_to_add_one_side >= 0):
                start -= length_to_add_one_side
        # print(start, end, prune_start, prune_end)
        if (not prune_start and not prune_end):
            start -= length_to_add_one_side
            end += length_to_add_one_side
            
        locs = [list(x) for x in locs]
        locs[0][0] = start
        locs[length - 1][1] = end
        
        notes["padded_merged_regex_location"][i] = locs

def character_cleaning(notes):
    notes['regex_matches'] = notes['regex_matches'].astype(str)
    notes['regex_matches'] = notes['regex_matches'].str.replace("\[\]", '')

    notes['padded_regex_sent'] = notes['padded_regex_sent'].astype(str)
    notes['padded_regex_sent'] = notes['padded_regex_sent'].str.replace('[', '')
    notes['padded_regex_sent'] = notes['padded_regex_sent'].str.replace(']', '')

    notes = notes.dropna(subset=["padded_regex_sent"])
    notes['padded_regex_sent'] = notes['padded_regex_sent'].str.replace('"', "'")

def note_preprocessing(note):
    # note = re.sub('[^A-Za-z0-9]+', '', note)
    note = re.sub(r'   • ', ' ; ', note)
    note = re.sub(r'[ ]{4,}', ' ', note)
    note = re.sub(r'  ', '\n', note)
    note = re.sub(r'    ', '\n\n', note)

    return note

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

    # pulling context windows
    seqs = []
    for i in range(len(notes)):
        seqs.append(pull_context_windows(notes, i, "merged_row_location"))
    notes["regex_sent"] = seqs

    # tokenizing sequences into ClincalBERT tokens 
    token_lens = []
    for i in (range(len(notes))):
        token_lens.append(clinical_bert_tokenize(notes, i, "regex_sent"))
    notes["token_length"] = token_lens
    
    # padding all Sequences such that they are as close as possible to 512 ClincialBERT Tokens
    notes["padded_merged_regex_location"] = notes["merged_row_location"].copy()
    notes["sequence_length"] = notes["regex_sent"].astype(str).map(len)
    for i in (range(len(notes))):
        notes["padded_merged_regex_location"][i] = list(notes["padded_merged_regex_location"][i])

    for i in (range(len(notes))):
        generate_padded_context_windows(notes, i)

    # pulling padded context windows
    padded_seqs = []
    for i in (range(len(notes))):
        padded_seqs.append(pull_context_windows(notes, i, "padded_merged_regex_location"))
    notes["padded_regex_sent"] = padded_seqs

    # minor cleaning
    character_cleaning(notes)

    # regex substitutions
    for i in (range(len(notes))):
        notes.at[i, "padded_regex_sent_preprocessed"] = note_preprocessing(notes.at[i, "padded_regex_sent"])

    return notes 

# def tester():
#     notes = sequence_extraction_pipeline(r"C:\Users\tanis\OneDrive - Phillips Exeter Academy\Data\Programming\APOE-SLAT\Web-Tool\app\gui\static\test_notes.txt")
#     notes.to_csv(r"static/test_sequences.csv", index = False)

# tester()