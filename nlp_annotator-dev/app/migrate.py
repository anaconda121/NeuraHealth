# migrate when you change the schema (i.e. framework for database)
# when you change values, no need to remigrate

# python manage.py makemigrations
# python manage.py migrate
# python manage.py shell

from gui.models import PatientDemographic, PatientYear, Note, Timeline

# n = Note.objects.get(PATIENT_NUM=1)
# n.IDX = 1  # change field
# n.save() # this will update only