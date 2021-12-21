from django import template
from django.utils import html
import regex as re

register = template.Library()

@register.filter(name = 'filter_note')
def filter_note(notelist, pk):
    # filters notes by patient ID
    return notelist.filter(PatientID = pk)

@register.filter(name = 'filter_patient_year')
def filter_patient_year(patientyearlist, pk):
    # filters notes by patient ID
    return patientyearlist.filter(PatientID = pk)


@register.filter(name = 'get_age')
def get_age(patient, notelist):

    birth = patient.BirthDTS
    first_contact = notelist[0].ContactDTS

    if first_contact is not None and birth is not None: 
        age_at_encounter = first_contact - birth
        years_at_encounter = divmod(age_at_encounter.days, 365)[0]
        return(str(years_at_encounter) + " YR")
    else:
        return("Unavailable")

@register.filter(name = 'get_sex')
def get_sex(patient):
    return(patient.SexDSC[0])


# for the note level annotation; this feature is not currently used
@register.filter(name = 'fill_table')
def fill_table(note):
    return("#F1F1F1")
    # if note.Label == "0":
    #     return("#D1E7DD")
    # elif note.Label == "1":
    #     return("#F8D7DA")
    # else:
    #     return("#F1F1F1")


@register.filter(name = 'fill_patient_table')
def fill_patient_table(patient):
    if patient.CognitiveConcern == "No Cognitive Concern":
        return("#D1E7DD")
    elif patient.CognitiveConcern == "Cognitive Concern":
        return("#F8D7DA")
    elif patient.CognitiveConcern == "Undetermined":
        return("#E4D5C8")
    else:
        return("#F1F1F1")


@register.filter(name = 'fill_patient_collapsible')
def fill_patient_collapsible(patient):
    if patient.CognitiveConcern == "No Cognitive Concern":
        return("background-color: #5FAB88; --my-hover-var: #BCDCCD;")
    elif patient.CognitiveConcern == "Cognitive Concern":
        return("background-color: #E0525D; --my-hover-var: #F3B9BF;")
    elif patient.CognitiveConcern == "Undetermined":
        return("background-color: #AE825B; --my-hover-var: #DDCABB;")
    else:
        return("background-color: #777777; --my-hover-var: #D6D6D6;")
    
    # if patient.SyndromicDiagnosis == "0":
    #     return("#D1E7DD")
    # elif patient.SyndromicDiagnosis == "1":
    #     return("#FFF3CD")
    # elif patient.SyndromicDiagnosis == "2":
    #     return("#F8D7DA")
    # else:
    #     return("#F1F1F1")


@register.filter(name = 'fill_cc_form')
def fill_cc_form(patient):
    if patient.CognitiveConcern == "Not Yet Annotated":
        return("opacity: 1;")
    else:
        return("opacity: 0.5; filter: grayscale(100%);")
        # return("opacity: 0.6; filter: blur(0.7px) blur(0.5px);")

@register.filter(name = 'fill_si_form')
def fill_si_form(patient):
    if patient.StageImpairment == "Not Yet Annotated":
        return("opacity: 1;")
    else:
        return("opacity: 0.5; filter: grayscale(100%);")
        # return("opacity: 0.6; filter: blur(0.7px) blur(0.5px);")

# @register.filter(name = 'redact')
# def redact(value):
#      return value.replace('XXXXX', '<span class="redact">XXXXX</span>')

# REPLACE XXXXX WITH BLACK TEXT
@register.filter("redact")
def redact(privateinfo):    
    if privateinfo is not None:
        return  html.mark_safe(privateinfo.replace('XXXXX', '<span class="redact">XXXXX</span>'))
    else:
        return  html.mark_safe("None")

@register.filter("trunc_redact")
def trunc_redact(value, max_length):
    if value is not None:
        if len(value) > max_length:
            trunc_val = value[:max_length]
            if not len(value) == max_length+1 and value[max_length+1] != " ":
                trunc_val = trunc_val[:trunc_val.rfind(" ")]
            trunc_val += "..."
        else:
            trunc_val = value
        return  html.mark_safe(trunc_val.replace('XXXXX', '<span class="redact">XXXXX</span>'))
    else:
        return  html.mark_safe("None")

# <!-- <td><a href="/annotate/{{patient.PatientID}}/{{noteDB_over_year|get_first_note_py:"patient.PatientID, py.Year"}}>{{py.Year}}</a></td> -->
# @register.filter(name = 'get_first_note_py')
# def get_first_note_py(notelist, grp_args): # pk, yr
#     pk, yr = grp_args.split(',')
#     # retrieves LocalNoteID (i.e. index) of first note in a specified year for a specified patient
#     # return notelist.filter(PatientID = pk).get(Year = yr).LocalNoteID
#     return 1