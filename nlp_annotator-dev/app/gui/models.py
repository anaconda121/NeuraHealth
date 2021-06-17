import re

from django.db import models

# to reset databsae:
    # run python manage.py reset_db (from django-extensions package)

# to delete all data from the table:
# python manage.py shell
# >> from gui.models import PatientDemographic, PatientYear, Note
# >> PatientDemographic.objects.all().delete()
# >> PatientYear.objects.all().delete()
# >> Note.objects.all().delete()

# to add data:
# update .csv files in load_data/data
# python manage.py shell
# >> %run load_data/load_data.py

# each element in choices is a tuple of actual value to be stored, then human readable translation
# in our case, these are the same

BaseModel = models.Model


class Sentence(BaseModel):
    Contents = models.TextField(blank = False, null = False)
    Note = models.ForeignKey("gui.Note", null = False, on_delete=models.PROTECT)

class SentenceAssignment(BaseModel):
    User = models.ForeignKey("accounts.CustomUser", null = False, on_delete=models.PROTECT)
    Sentence = models.ForeignKey("gui.Sentence", null = False, on_delete=models.PROTECT)
    CompletedAt = models.DateTimeField(null=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['User', 'Sentence'], name='uq_assignment')
        ]

class SentenceAnnotation(BaseModel):
    class AnnotationLabel(models.TextChoices):
        YES = 'YES', "Yes"
        NO = 'NO', "No"
        NEITHER = 'NTR', "Neither"
    
    Sentence = models.ForeignKey("gui.Sentence", null = False, on_delete=models.PROTECT)
    Label = models.CharField(max_length=3, choices=AnnotationLabel.choices, null = False)
    Annotator = models.ForeignKey("accounts.CustomUser", null = False, on_delete=models.PROTECT)

class SeedRegex(BaseModel):
    Pattern = models.TextField(blank = False, null = False, unique = True)

    @property
    def regex(self):
        return re.compile(self.Pattern, flags=re.IGNORECASE)

class SentenceSeedRegex(BaseModel):
    Sentence = models.ForeignKey("gui.Sentence", null = False, on_delete=models.PROTECT)
    SeedRegex = models.ForeignKey("gui.SeedRegex", null = False, on_delete=models.PROTECT)

class AlwaysRegex(BaseModel):
    class AnnotationLabel(models.TextChoices):
        YES = 'Y', 'Always Yes'
        NO = 'N', 'Always No'
        NEITHER = 'T', 'Always Neither'

    Pattern = models.TextField(blank = False, null = False, unique = True)
    Annotation = models.CharField(max_length=1, choices=AnnotationLabel.choices, null = False)
    CreatedBy = models.ForeignKey("accounts.CustomUser", null = False, on_delete=models.PROTECT)
    
    @property
    def regex(self):
        return re.compile(self.Pattern, flags=re.IGNORECASE)

class SentenceAlwaysRegex(BaseModel):
    Sentence = models.ForeignKey("gui.Sentence", null = False, on_delete=models.PROTECT)
    AlwaysRegex = models.ForeignKey("gui.AlwaysRegex", null = False, on_delete=models.PROTECT)

class PatientDemographic(models.Model):
    PatientID = models.TextField(blank = True, null = False, unique = True)
    MRN = models.TextField(blank = True, null = True)
    EMPI = models.TextField(blank = False, null = False)
    
    def __str__(self):
        return(str(self.PatientID))

class Note(models.Model):
    PatientID = models.TextField(blank = True, null = True)
    PatientEncounterID = models.CharField(max_length = 100, blank = True, null = True)
    NoteID = models.TextField(blank = True, null = True, unique = True)
    Date = models.DateField(null = False)


    def __str__(self):
        return(str(self.PatientID) + "/" + str(self.LocalNoteID))
