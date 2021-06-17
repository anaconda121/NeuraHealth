from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import Form, ModelForm, Textarea
from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import FilteredRelation, Q, Count
from django.db import IntegrityError
import json
import regex as re
import functools
import datetime
from time import sleep
from collections import Counter
from itertools import chain, cycle
import itertools
from .models import (
    PatientDemographic, 
    Sentence, 
    SentenceAssignment, SentenceAnnotation, AlwaysRegex, 
    SentenceAlwaysRegex, SentenceSeedRegex
)
from accounts.forms import SignUpForm
from django.contrib import messages

from accounts.models import CustomUser

#reading in headers
import pandas as pd

# log-in and sign-up forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required


def custom_error_404(request, exception):
    template = loader.get_template('gui/error.html')
    context = {'exception': "404"}
    print("404 for: ", request)
    return HttpResponse(template.render(context, request), status, status=404)

def custom_error_500(request):
    template = loader.get_template('gui/error.html')
    context = {'exception': "500"}
    print("500 for: ", request)
    return HttpResponse(template.render(context, request), status=500)

def custom_error_403(request, exception):
    template = loader.get_template('gui/error.html')
    context = {'exception': "403"}
    print("403 for: ", request)
    return HttpResponse(template.render(context, request), status=403)

## INDEX VIEW
def index(request):

    # retrieve information of currently logged in user
    current_user = request.user

    # redirect to either annotator home or login page
    if current_user.is_authenticated:
        return redirect('/home')
    else:
        return redirect('/login')


### ABOUT PAGE
def about(request):

     # get template from gui/profile.html
    template = loader.get_template('gui/about.html')

    email_form = "Name:%0D%0AFeature Request:"

    context = {'email_form': email_form}

    return HttpResponse(template.render(context, request))


## USER LOGIN VIEW
def user_login(request):

    # get template from gui/login.html
    template = loader.get_template('gui/login.html')

    # define sign up and log in forms
    signup_form = SignUpForm(request.POST)
    login_form = AuthenticationForm(data=request.POST)

    if request.method == 'POST':

        # check sign up form, log in user
        if signup_form.is_valid():
            user = signup_form.save()
            login(request, user)

            # # upon sign-up, assign five patients
            # unassigned = PatientDemographic.objects.filter(Assigned = False)[0:5]

            # # get patient IDs, update Assigned of PatientDemographic database to True
            # patientIDs = []
            # for patient in unassigned:
            #     patientIDs.append(patient.PatientID)
            #     patient.Assigned = True
            #     patient.save()

            # # save patient IDs in AssignedPatients variable for each user upon login
            # user.AssignedPatients = ', '.join([str(x) for x in patientIDs])
            # print("Patients Assigned: " + user.AssignedPatients)
            user.save()

            return redirect('/home')
        else:
            signup_form = SignUpForm()

        # check log in form
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            print("Log-In Success Message")
            messages.success(request, 'You are now logged in as ' + user.username + '.')
            return redirect('/home')
        else:
            login_form = AuthenticationForm()

        
        print("Sign-Up or Log-In Error Message")
        messages.error(request, 'The credentials entered are invalid. Please try again.')

    context = {
        'signup_form': signup_form,
        'login_form': login_form
    }

    return HttpResponse(template.render(context, request))


### USER LOGOUT
@login_required(redirect_field_name = None)
def user_logout(request):
    # if request.method == 'POST':
    #     logout(request)
    logout(request)    
    return redirect('/login')


### USER PROFILE
@login_required(redirect_field_name = None)
def user_profile(request):

     # get template from gui/profile.html
    template = loader.get_template('gui/profile.html')

    current_user: CustomUser = request.user

    # retrieve and parse assigned IDs
    assignedIDs = [p.PatientID for p in current_user.assigned_patients]
    full_note_count = Note.objects.filter(PatientID__in = assignedIDs).count()
    full_patient_count = PatientDemographic.objects.filter(PatientID__in = assignedIDs).count()

    # get notes with completed annotations
    noteDB = Note.objects.filter(Annotator = current_user.username).exclude(Label = "Not Yet Annotated")
    annot_patients = []
    for annot_notes in noteDB:
        annot_patients.append(annot_notes.PatientID)
    annot_patients = list(set(annot_patients)) # convert to set to remove duplicate patient IDs

    note_patientDB = PatientDemographic.objects.filter(PatientID__in = annot_patients) # subset patients which have SOME completed notes, NOT ALL COMPLETED PATIENTS
    
    completed_note_count = noteDB.count()
    no_notes = completed_note_count == 0

    # get all completed patients
    patientDB = PatientDemographic.objects.filter(Annotator = current_user.username).exclude(CognitiveConcern = "Not Yet Annotated")
    complete_patients = []
    for my_patient in patientDB:
        complete_patients.append(my_patient.PatientID)
    complete_patients = list(set(complete_patients))
    fullnoteDB = Note.objects.filter(PatientID__in = complete_patients).order_by("-KeywordCount")

    completed_patient_count = patientDB.count()
    no_patients = completed_patient_count == 0

    # get account keywords
    keywords_raw = current_user.Keywords

    # form to update keywords
    keywords_form = KeywordForm(initial = {'keywords': keywords_raw})
    if request.method == 'POST':
        keywords_form  = KeywordForm(request.POST)
        if keywords_form.is_valid():
            keywords_raw = keywords_form['keywords'].value()
            print("Keywords: " + keywords_raw)
            current_user.Keywords = keywords_raw
            current_user.save()
            messages.success(request, 'Keywords updated for your account.')
            return redirect('/profile')

    context = {
        'current_user': current_user,
        
        'noteDB': noteDB,
        'note_patientDB': note_patientDB,
        'completed_note_count': completed_note_count,
        'full_note_count': full_note_count,
        'no_notes': no_notes,

        'patientDB': patientDB,
        'fullnoteDB': fullnoteDB,
        'completed_patient_count': completed_patient_count,
        'full_patient_count': full_patient_count,
        'no_patients': no_patients,

        'keywords_form': keywords_form,
        'keywords_raw': keywords_raw,
    }

    return TemplateResponse(request, template, context=context)


### CONSENSUS VIEW
@login_required(redirect_field_name = None)
def group_consensus(request):

    # get template from gui/consensus.html
    template = loader.get_template('gui/consensus.html')

    # get note and patient databases
    patientDB = PatientDemographic.objects.filter(Consensus = True) # subset patients which are assigned
    consensusIDs = [x.PatientID for x in patientDB]
    noteDB = Note.objects.filter(PatientID__in = consensusIDs) # subset notes of those patients

    # calculate statistics for notes
    noteTODO = noteDB.filter(Label = "Not Yet Annotated")
    total_notes = noteDB.count()
    todo_notes = noteTODO.count()
    completed_notes = total_notes - todo_notes
    notes_per = round(todo_notes / total_notes * 100) if total_notes != 0 else 0

    no_notes = total_notes == 0

    # calculate statistics for patient-year
    patientTODO = patientDB.filter(CognitiveConcern = "Not Yet Annotated")
    total_patients = patientDB.count()
    todo_patients = patientTODO.count()
    completed_patients = total_patients - todo_patients
    patients_per = round(todo_patients / total_patients * 100) if total_patients != 0 else 0


    context = {
            'patientDB': patientDB,
            'noteDB': noteDB, 
            'noteTODO': noteTODO, 'total_notes': total_notes, 'todo_notes': todo_notes, 'completed_notes': completed_notes, 'notes_per': notes_per, 'no_notes': no_notes,
            'patientTODO': patientTODO, 'total_patients': total_patients, 'todo_patients': todo_patients, 'completed_patients': completed_patients, 'patients_per': patients_per,
    }

    return HttpResponse(template.render(context, request))



### CONSENSUS VIEW
@login_required(redirect_field_name = None)
def search(request):

    # get template from gui/search.html
    template = loader.get_template('gui/search.html')

    # get note and patient databases
    patientDB = PatientDemographic.objects.filter(Consensus = True) # subset patients which are assigned
    consensusIDs = [x.PatientID for x in patientDB]
    noteDB = Note.objects.filter(PatientID__in = consensusIDs) # subset notes of those patients
    
    context = {
            'patientDB': patientDB,
            'noteDB': noteDB,
    }

    return HttpResponse(template.render(context, request))


# form to request additional patients for dashboard view
class ManualLabelForm(Form):
    manual_label_choices = [
        ('y', 'Yes'),
        ('n', 'No'),
        ('t', 'Neither')
    ]
    label = forms.ChoiceField(widget=forms.RadioSelect, choices=manual_label_choices, label="")
    

class AlwaysRegexForm(Form):
    yes_patterns = forms.CharField(widget=forms.Textarea, required=False)
    no_patterns = forms.CharField(widget=forms.Textarea, required=False)
    neither_patterns = forms.CharField(widget=forms.Textarea, required=False)

    def clean(self):
        cleaned_data = super().clean()
        yes, no, neither = (
            cleaned_data['yes_patterns'].split("\n"),
            cleaned_data['no_patterns'].split("\n"),
            cleaned_data['neither_patterns'].split("\n")
        )
        yes, no, neither = (
            filter(lambda x: bool(x), yes),
            filter(lambda x: bool(x), no),
            filter(lambda x: bool(x), neither)
        )
        yes, no, neither = set(yes), set(no), set(neither)
        print("patterns", yes, no, neither)
        self.cleaned_data['yes_patterns'] = yes
        self.cleaned_data['no_patterns'] = no
        self.cleaned_data['neither_patterns'] = neither
        if not yes and not no and not neither:
            self.error_message = "Must specify one or more patterns!"
            raise ValueError("AlwaysRegexForm is not valid!")
        all_patterns = Counter(filter(lambda x: bool(x), itertools.chain(yes, no, neither)))
        print(all_patterns)
        if max(all_patterns.values()) > 1:
            self.error_message = "Cannot specify duplicate patterns!"
            raise ValueError("AlwaysRegexForm is not valid!")


## ANNOTATOR HOME VIEW /home
@login_required(redirect_field_name = None)
def annotator_home(request):
    
    # get template from gui/home.html
    template = loader.get_template('gui/home.html')

    # retrieve information of currently logged in user
    current_user: CustomUser = request.user

    assignments = SentenceAssignment.objects.filter(User=current_user).order_by('id')
    completed = assignments.filter(CompletedAt__isnull=False).count()
    try:
        next_sentence = assignments.filter(CompletedAt__isnull=True)[0]
        sentence = next_sentence.Sentence
    except (IndexError, ObjectDoesNotExist) as e:
        sentence = None

    if not sentence:
        return render(request, "gui/no_sentence.html")

    if request.method == 'POST':
        formType = request.POST['formType']
        sentenceId = request.POST['sentenceId']
        if formType == 'manualLabel':
            form = ManualLabelForm(request.POST)
            if form.is_valid():
                label = form.cleaned_data['label']
                if label == 'y':
                    label = SentenceAnnotation.AnnotationLabel.YES
                elif label == 'n':
                    label = SentenceAnnotation.AnnotationLabel.NO
                elif label == 't':
                    label = SentenceAnnotation.AnnotationLabel.NEITHER
                sentence = Sentence.objects.get(pk=sentenceId)
                annotation = SentenceAnnotation(
                    Sentence=sentence, 
                    Annotator=current_user, 
                    Label=label
                )
                annotation.save()
                assignment = SentenceAssignment.objects.get(Sentence=sentence, User=current_user)
                assignment.CompletedAt = datetime.datetime.utcnow()
                assignment.save()
                messages.success(request, 'Labeled!')
                return redirect("/home")
        elif formType == 'regex':
            form = AlwaysRegexForm(request.POST)
            try:
                if form.is_valid():
                    data = form.cleaned_data
                    print("applying regex")
                    counts = _apply_patterns(current_user, data['yes_patterns'], data['no_patterns'], data['neither_patterns'])
                    context = {
                        "patterns": counts
                    }
                    return render(request,"gui/regex_result.html", context=context)
            except ValueError as e:
                messages.error(request, form.error_message)
                
    matching_seeds = SentenceSeedRegex.objects.filter(Sentence=sentence).prefetch_related('SeedRegex')

    label_form = ManualLabelForm()
    regex_form = AlwaysRegexForm()
    context = {
            'current_user': current_user,
            'sequenceNumber': completed + 1,
            'sentenceCount': assignments.count(),
            'currentSentence': sentence, 
            'matchingPatterns': [r.SeedRegex for r in matching_seeds],
            'labelForm': label_form,
            'regexForm': regex_form
    }

    return HttpResponse(template.render(context, request))


def _apply_pattern(user, pattern, label):
    regex = AlwaysRegex(Pattern=pattern, Annotation=label, CreatedBy=user)
    try:
        regex.save()
        count = _check_sentences(regex)
    except IntegrityError:
        count = -1
    return {
        "pattern": pattern,
        "label": str(regex.Annotation.label),
        "count": count if count > -1 else "Duplicate pattern, not applied"
    }

def _check_sentences(regex):
    uncompleted_sentences = Sentence.objects.annotate(
        regex=Count('sentencealwaysregex'),
        annotation=Count('sentenceannotation')
    ).filter(Q(regex__lt=1), Q(annotation__lt=1))
    count = 0
    print("found", uncompleted_sentences.count(), "uncompleted sentences")
    for sentence in uncompleted_sentences:
        if regex.regex.search(sentence.Contents):
            application = SentenceAlwaysRegex(Sentence=sentence, AlwaysRegex=regex)
            application.save()
            assignments = SentenceAssignment.objects.filter(Sentence=sentence, CompletedAt__isnull=True)
            completed_at = datetime.datetime.utcnow()
            for assignment in assignments:
                assignment.CompletedAt = completed_at
            SentenceAssignment.objects.bulk_update(assignments, ['CompletedAt'])
            count += 1
    return count

def _apply_patterns(user, yes, no, neither):
    results = []
    for pattern in yes:
        applied = _apply_pattern(user, pattern, AlwaysRegex.AnnotationLabel.YES)
        results.append(applied)
    for pattern in no:
        applied = _apply_pattern(user, pattern, AlwaysRegex.AnnotationLabel.NO)
        results.append(applied)
    for pattern in neither:
        applied = _apply_pattern(user, pattern, AlwaysRegex.AnnotationLabel.NEITHER)
        results.append(applied)
    return results

@csrf_exempt
def highlight_sentence(request):
    body = json.loads(request.body)
    sentence = body['text']
    yes = filter(lambda x: bool(x), body['yesPatterns'].strip().split("\n"))
    no = filter(lambda x: bool(x), body['noPatterns'].strip().split("\n"))
    neither = filter(lambda x: bool(x), body['neitherPatterns'].strip().split("\n"))
    data = {
        "text": _highlight_patterns(sentence, yes, no, neither)
    }
    return JsonResponse(data)

def _highlight_patterns(text, yes_patterns, no_patterns, neither_patterns):
    for pattern in yes_patterns:
        text = re.sub(pattern, highlight("yes-pattern"), text, flags=re.IGNORECASE)
    for pattern in no_patterns:
        text = re.sub(pattern, highlight("no-pattern"), text, flags=re.IGNORECASE)
    for pattern in neither_patterns:
        text = re.sub(pattern, highlight("neither-pattern"), text, flags=re.IGNORECASE)
    return text

# HIGHLIGHT FUNCTION
def highlight(span_class):
    return(lambda match_group: r'<span class = "' + span_class + r'">' + match_group.group(0) + r'</span>')

# DEFAULT KEYWORD HIGHLIGHT FUNCTION
def keyword_count(output, keywords_raw, is_note = False):

    keywords = keywords_raw.split(", ") # read comma separated user keywords
    regex_raw = open("gui/static/regex_default.txt", mode = "r", encoding = 'utf-8').read().split("\n") # get regex expressions from file in static folder
    regex_raw = regex_raw + keywords # combine default and user-specified keywords
    regex_list = [re.compile(regex,flags=re.IGNORECASE) for regex in regex_raw] # compile regex list
    
    span_class = "note-keyword" if is_note else "keyword"

    for pattern in regex_list:
        output = re.sub(pattern, highlight(span_class), output)

    return output

# ADL KEYWORD HIGHLIGHT FUNCTION
def adl_count(output, is_note = False):

    regex_raw = open("gui/static/regex_adl.txt", mode = "r", encoding = 'utf-8').read().split("\n") # get regex expressions from file in static folder
    regex_list = [re.compile(regex,flags=re.IGNORECASE) for regex in regex_raw] # compile regex list
    
    span_class = "note-adl" if is_note else "adl"

    for pattern in regex_list:
        output = re.sub(pattern, highlight(span_class), output)

    return output

# SPLIT BY HEADERS FUNCTION
def format_note(output):

    # split by sentences
    # output = re.sub(r"(?<![A-Z][a-z])([!?.])(?=\s*[A-Z])\s*", r"\1\n<br>", output)

    headers = open("gui/static/regex_headers.txt", mode = "r", encoding = 'utf-8').read().split("\n")
    header_list = [re.compile(regex, flags=re.IGNORECASE) for regex in headers]
    # print(header_list)

    # check if the first word in the sentence is a word from the headers file
    # if it is, then add an extra breakpoint before it

    pattern_list = [re.findall(pattern, output) for pattern in header_list]
    pattern_list = set(list((chain.from_iterable(pattern_list)))) # flatten list, remove duplicates

    tups = [(itm, r'<br><br><span style="text-decoration: underline;">' + itm + r'</span>') for itm in pattern_list]

    for old, new in tups:
        output = re.sub(old, new, output)

    return output


# SPLIT BY BULLETS FUNCTION
def format_bullet(output):

    bullets = open("gui/static/regex_bullets.txt", mode = "r", encoding = 'utf-8').read().split("\n")
    bullet_list = [re.compile(regex, flags=re.IGNORECASE) for regex in bullets]

    pattern_list = [re.findall(pattern, output) for pattern in bullet_list]
    pattern_list = set(list((chain.from_iterable(pattern_list)))) # flatten list, remove duplicates

    tups = [(itm, r'<br>' + itm) for itm in pattern_list]

    for old, new in tups:
        output = re.sub(old, new, output)

    return output


# # REPLACE XXXXX WITH GRAY BOX FOR PRIVATE INFO
# def redact(privateinfo):
#     private_flag = re.compile("XXXXX") # replace regex
#     pattern_list = re.findall(private_flag, privateinfo)
#     pattern_list = set(list((chain.from_iterable(pattern_list)))) # flatten list, remove duplicates
#     tups = [(itm, r'<span class="redact">' + itm + r'</span>') for itm in pattern_list]
#     # make the substitution to add highlight tag
#     for old, new in tups:
#         privateinfo = re.sub(old, new, privateinfo)
#     return privateinfo


# PARSE LABS/IMAGING BY REPLACING | WITH NEW LINE
def parse_labs(labs):
    return r'<tr><td>' + labs.replace('%^%', r'</td></tr><tr><td>') + r'</td></tr>'

def parse_labs_cell(labs):
    return labs.replace('%&%', r'</td><td>')


## ANNOTATOR PANEL VIEW
@login_required(redirect_field_name = None)
def show_note(request, patient_id, local_note_id):
    
    # get template from gui/note.html
    template = loader.get_template('gui/note.html')

    # retrieve information of currently logged in user
    current_user = request.user

    # use the parameters from URl slug to get all notes for specified patient, then select correct note from Note database
    notes_patient = Note.objects.filter(PatientID = patient_id)
    note = notes_patient.get(LocalNoteID = local_note_id)

    # get index for note in year
    notes_patient_year = notes_patient.filter(Year = note.Year)
    year_idx = []
    for my_note in notes_patient_year:
        year_idx.append(my_note.LocalNoteID)
    patient_year_idx = str(year_idx.index(local_note_id) + 1) # zero indexed

    # select correct patient corresponding to specified note from PatientDemographic databse
    patient = PatientDemographic.objects.get(PatientID = patient_id)

    # use the parameters from URl slug to get timeline records for specified patient
    # timeline = Timeline.objects.filter(PatientID = patient_id)

    # get correct the patient year record from PatientYear database
    patient_year_all = PatientYear.objects.filter(PatientID = patient_id)
    patient_year = patient_year_all.get(Year = note.Year) # get appropriate patient year record

    # get all years for this patient, remove None values    
    all_years = []
    for year in patient_year_all:
        if year.Year is not None: all_years.append(year.Year)
    all_years.sort()

    # find next patient ID
    current_year_idx = all_years.index(note.Year) if note.Year is not None else len(all_years)
    previous_year_idx = notes_patient.filter(Year = all_years[current_year_idx - 1])[0].LocalNoteID if current_year_idx > 0 else local_note_id
    next_year_idx = notes_patient.filter(Year = all_years[current_year_idx + 1])[0].LocalNoteID if current_year_idx < len(all_years) - 1 else local_note_id

    # get note year, note count
    note_year = str(note.Year)[0:4]
    note_count = notes_patient.count()

    # calculate current age
    show_age = True
    if note.ContactDTS is not None and patient.BirthDTS is not None: 
        age_at_encounter = note.ContactDTS - patient.BirthDTS
        years_rem = divmod(age_at_encounter.days, 365)
        years_at_encounter = years_rem[0]
        months_at_encounter = divmod(years_rem[1], 30)[0]
    else:
        years_at_encounter = "NA"
        months_at_encounter = "NA"
        show_age = False

    output = str(note.NoteTXT) # note text
    current_meds = str(patient_year.CurrentMeds) # current medications
    med_hist = str(patient_year.MedHistory) # medication history
    
    pcc_note = str(patient.CoordinationNote) # patient care coordination note
    icd_codes = str(patient_year.ICDCodes)
    labs = str(patient.PatientLabs) # patient labs
    imaging = str(patient.PatientImaging) # patient imaging

    # format note
    output = format_bullet(output)
    output = format_note(output)
    # output = redact(output) # redact in template using templatetag

    # REGULAR KEYWORDS

    keywords_raw = current_user.Keywords
    output = keyword_count(output, keywords_raw, True) # apply keyword_count function above for note text
    note_keywords = output.count('<span class = "note-keyword">')

    current_meds = keyword_count(current_meds, keywords_raw) # for current medications
    med_hist = keyword_count(med_hist, keywords_raw) # for medication history

    pcc_note = keyword_count(pcc_note, keywords_raw) # apply keyword highlighting above for coordination note
    icd_codes = keyword_count(icd_codes, keywords_raw)
    labs = keyword_count(labs, keywords_raw) # for labs
    imaging = keyword_count(imaging, keywords_raw) # for imaging

    # ADL KEYWORDS

    output = adl_count(output, True) # apply keyword_count function above for note text

    current_meds = adl_count(current_meds) # for current medications
    med_hist = adl_count(med_hist) # for medication history

    pcc_note = adl_count(pcc_note) # apply keyword highlighting above for coordination note
    icd_codes = adl_count(icd_codes)
    labs = adl_count(labs) # for labs
    imaging = adl_count(imaging) # for imaging



    labs = parse_labs_cell(parse_labs(labs))
    imaging = parse_labs_cell(parse_labs(imaging))

    # get scratchpad text
    scratchpad_raw = patient.Scratchpad

    # get current consensus label
    patient_consensus = patient.Consensus

    # for previous and next buttons
    current_link = '/annotate/' + str(patient_id) + '/' + str(local_note_id)
    previous_link = '/annotate/' + str(patient_id) + '/' + str(local_note_id - 1) if local_note_id > 1 else current_link
    next_link = '/annotate/' + str(patient_id) + '/' + str(local_note_id + 1) if local_note_id < note_count  else current_link

    previous_year_link = '/annotate/' + str(patient_id) + '/' + str(previous_year_idx)
    next_year_link = '/annotate/' + str(patient_id) + '/' + str(next_year_idx)


    # POST user input using NoteForm to save annotation labels
    # note_form = NoteForm(instance = note)
    # if request.method == 'POST':
    #     note_form = NoteForm(request.POST, instance = note)
    #     if note_form.is_valid():
    #         note_form.save()
    #         note.Annotator = current_user.username
    #         note.DateAnnotated = datetime.datetime.now()
    #         note.save()
    #         messages.success(request, 'You have sucessfully annotated Note #' + str(local_note_id) + ' for Patient #' + str(patient_id) + '.')
    #         return redirect(current_link) # go to same note
    

    # POST user input for cognitive concern
    cc_form = CognitiveConcernForm(instance = patient)
    if request.method == 'POST':
        cc_form = CognitiveConcernForm(request.POST, instance = patient)
        if cc_form.is_valid():
            cc_form.save()
            patient.Annotator = current_user.username
            patient.DateAnnotated = datetime.datetime.now()
            patient.save()
            messages.success(request, 'You have sucessfully annotated cognitive concern for Patient #' + str(patient_id) + '.')
            return redirect(current_link)

    # POST user input for cognitive concern
    si_form = StageImpairmentForm(instance = patient)
    if request.method == 'POST':
        si_form = StageImpairmentForm(request.POST, instance = patient)
        if si_form.is_valid():
            si_form.save()
            patient.save()
            messages.success(request, 'You have sucessfully annotated stage of impairment for Patient #' + str(patient_id) + '.')
            return redirect(current_link)


    # # POST user input using PatientForm to save annotation labels
    # patient_form = PatientForm(instance = patient)
    # if request.method == 'POST':
    #     patient_form = PatientForm(request.POST, instance = patient)
    #     if patient_form.is_valid():
    #         patient_form.save()
    #         patient.Annotator = current_user.username
    #         patient.DateAnnotated = datetime.datetime.now()

    #         # if no cognitive concern or unknown, severity is not applicable
    #         if (patient.SyndromicDiagnosis == "0" | patient.SyndromicDiagnosis == "1"):
    #             patient.CINDSeverity = "N/A"
    #             patient.DementiaSeverity = "N/A"

    #         # clear severity label for other syndromic diagnosis
    #         if (patient.SyndromicDiagnosis == "2"):
    #             patient.DementiaSeverity = "N/A"

    #         # clear severity label for other syndromic diagnosis
    #         if (patient.SyndromicDiagnosis == "3"):
    #             patient.CINDSeverity = "N/A"

    #         patient.save()
    #         messages.success(request, 'You have sucessfully annotated Patient #' + str(patient_id) + '.')
    #         return redirect(current_link)


    # form to dynamically update keywords
    keywords_form = KeywordForm(initial = {'keywords': keywords_raw})
    if request.method == 'POST':
        keywords_form  = KeywordForm(request.POST)
        if keywords_form.is_valid():
            keywords_raw = keywords_form['keywords'].value()
            print("Keywords: " + keywords_raw)
            output = keyword_count(output, keywords_raw) # note text regex highlighting
            current_meds = keyword_count(current_meds, keywords_raw) # current medications regex highlighting
            med_hist = keyword_count(med_hist, keywords_raw) # medication history regex highlighting
            current_user.Keywords = keywords_raw
            current_user.save()
            messages.success(request, 'Keywords updated.')
            return redirect(current_link)


    # form for scratchpad
    scratchpad_form = ScratchpadForm(initial = {'scratchpad': scratchpad_raw})
    if request.method == 'POST':
        scratchpad_form = ScratchpadForm(request.POST)
        if scratchpad_form.is_valid():
            scratchpad_raw = scratchpad_form['scratchpad'].value()
            patient.Scratchpad = scratchpad_raw
            patient.save()
            messages.success(request, 'Scratchpad successfully updated.')
            return redirect(current_link)


        # TOGGLE patient consensus message
    consensus_form = ConsensusForm()
    if request.method == 'POST':
        consensus_form = ConsensusForm(request.POST)
        if consensus_form.is_valid():
            patient.Consensus = not patient.Consensus
            patient.ConsensusActor = str("Dr. " + current_user.first_name + " " + current_user.last_name + " (" + current_user.username + ")")
            patient.save()
            if (patient.Consensus):
                messages.success(request, 'You have sucessfully sent Patient #' + str(patient_id) + ' to consensus conference.')
            else:
                messages.success(request, 'You have sucessfully removed Patient #' + str(patient_id) + ' from consensus conference.')
            return redirect(current_link)

    context = {
        'current_user': current_user,
        'patient': patient,
        'note': note,
        'patient_year': patient_year,
        # 'timeline': timeline,
        'patient_ID': patient_id,
        'note_year': note_year,
        'patient_year_idx': patient_year_idx,
        'note_count': note_count,
        'years_at_encounter': years_at_encounter,
        'months_at_encounter': months_at_encounter,
        'show_age': show_age,
        'note_text': output,
        'note_keywords': note_keywords,
        'med_hist': med_hist,
        'current_meds': current_meds,
        'pcc_note': pcc_note,
        'icd_codes': icd_codes,
        'labs': labs,
        'imaging': imaging,
        # 'note_form': note_form,
        # 'patient_form': patient_form,
        'cc_form': cc_form,
        'si_form': si_form,
        'consensus_form': consensus_form,
        'patient_consensus': patient_consensus,
        'keywords_form': keywords_form,
        'keywords_raw': keywords_raw,
        'scratchpad_form': scratchpad_form,
        'previous_link': previous_link,
        'next_link': next_link,
        'previous_year_link': previous_year_link,
        'next_year_link': next_year_link,
        'notes_patient': notes_patient,
    }

    return HttpResponse(template.render(context, request))