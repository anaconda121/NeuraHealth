from django.contrib import admin, messages
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import PatientDemographic

# class PatientDemographicResource(resources.ModelResource):
#     class Meta:
#         model = PatientDemographic

# class PatientDemographicAdmin(ImportExportModelAdmin):
#     resource_class = PatientDemographicResource
#     list_display = ('PatientID', 'MRN', 'BirthDTS', 'EthnicGroupDSC',
#     'MaritalStatusDSC', 'SexDSC', 'EducationLevelDSC',
#     'CoordinationNote', 'PatientLabs', 'PatientImaging', 'RefillRequests', 'Assigned',
#     'CognitiveConcern', 'StageImpairment', 
#     # 'CognitiveConcern', 'SyndromicDiagnosis', 'CINDSeverity', 'DementiaSeverity',
#     'Annotator', 'DateAnnotated', 'Scratchpad', 'Consensus', 'ConsensusActor') 

# # register patient model
# admin.site.register(PatientDemographic, PatientDemographicAdmin)
