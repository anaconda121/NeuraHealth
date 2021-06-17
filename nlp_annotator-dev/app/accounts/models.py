from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    Phone = models.IntegerField(blank = True, null = True)
    # AssignedPatients is deprecated, do not use!
    AssignedPatients = models.TextField(blank = True, null = True, default='None')
    Keywords = models.TextField(blank = True, null = True, default='dementia')
    

    @property
    def assigned_patients(self):
        return self.patientassignment_set.all()

    def add_patients(self, unassigned: list):
        assignments = []
        for patient in unassigned:
            assignment = PatientAssignment(PatientID=patient.PatientID, User=self)
            assignments.append(assignment)
        self.patientassignment_set.add(*assignments, bulk=False)
        print(f"assigned {len(assignments)} to {self.username}")

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.username
