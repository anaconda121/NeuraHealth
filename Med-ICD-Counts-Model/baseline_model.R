library(glmnet)
library(ROCR)
library(tidyverse)
library(data.table)
library(lubridate)

# read in EDW data 
meds<-fread("data/medications.csv")
diagnoses <- fread('data/icd_diagnosis.csv')
diagnoses[,Date := ymd(ContactDTS)]
meds[,Date := ymd(OrderDTS)]

# date time filters
#diagnoses <- diagnoses[Date >= '2018-01-01' & Date <= '2018-12-31']
#meds <- meds[Medication_Date >= '2018-01-01' & Date <= '2018-12-31']

AD_Meds <- c("Galantamine", "Donepezil", "Rivastigmine", "Razadyne", "Razadyne ER", "Aricept", "Exelon","Namenda","Memantine");

meds[,AD := grepl(paste(AD_Meds, collapse="|"),MedicationDSC,ignore.case = T)]

diagnoses[,AD := (grepl("Dementia|Alzheimer's|cognitive impairment|memory loss|frontotemporal dementia",DiagnosisNM,ignore.case = TRUE) | grepl("^290|^294|^331|G30|G31|780.93",ICD9CD,ignore.case = TRUE) | grepl("^290|^294|^331|G30|G31|780.93",ICD10CD,ignore.case = TRUE)) & !grepl("hydrocephalus",DiagnosisNM,ignore.case = TRUE)];

structured_variables <- data.table(PatientID = unique(c(diagnoses$PatientID,meds$PatientID)))

structured_variables[diagnoses[AD==1,.N,by=.(PatientID)],on=.(PatientID),Dx_Count := i.N]
structured_variables[meds[AD==1,.N,by=.(PatientID)],on=.(PatientID),Med_Count := i.N]
structured_variables[is.na(structured_variables)] <- 0
structured_variables[,AD_Med_or_ICD_Code := ifelse(Dx_Count > 0 | Med_Count > 0,1,0)]


# tanish set 

tanish <- fread('data/20K_sample.csv')
# need EMPI for tanish's set, get from EDW data
tanish[rbindlist(list(meds,diagnoses),fill =T),on=.(patient_id = PatientID),EMPI := i.EMPI]
# 0 = no, 1 = neither, 2 = CI
tanish[,Binary_CI := ifelse(prediction == 2,1,0)]
# at least one CI, give 1 for patient level cognitive impairment 
tanish[,patient_CI := ifelse(sum(Binary_CI) > 0,1,0),by=.(patient_id)]
tanish[,num_sequences_patient := .N,by=.(patient_id)]

# one row per patient 
tanish_predictions <- tanish[,.SD[1],by=.(patient_id)][,.(patient_id,patient_CI,num_sequences_patient,EMPI)]
# merge structured data back on 
tanish_predictions[structured_variables,on=.(patient_id=PatientID),`:=` (Dx_Count = i.Dx_Count, Med_Count = i.Med_Count, AD_Med_or_ICD_Code = i.AD_Med_or_ICD_Code)]

# any missing data? NO
nrow(tanish_predictions[is.na(AD_Med_or_ICD_Code)])

# patient cognitive impairment by whether they have med/code 
tanish_predictions[,.N,by=.(patient_CI,AD_Med_or_ICD_Code)]

# read in APOE data 
apoe <- fread('data/apoe/Partners_biobank_APOE_nodup.csv')
bib <- rbindlist(list(fread('data/apoe/sd587_03212118253982866_6375194824947826181_Bib.txt'),fread('data/apoe/sd587_03212118253982866_6375194824947826182_Bib.txt')))
# join back EMPI from mapping
apoe[bib,on=.(subject_id = Subject_Id),EMPI := i.EMPI]

tanish_predictions[apoe,on=.(EMPI),APOE := i.APOE]

##### need collapsed APOE definition

tanish_predictions[,.N,by=.(patient_CI,AD_Med_or_ICD_Code,APOE)]

fwrite(tanish_predictions,file='data/tanish_predictions_with_structured_features.csv')

# view false negatives
View(tanish[patient_id %in% tanish_predictions[patient_CI == 0 & AD_Med_or_ICD_Code == 1,patient_id]])
#view false positives
View(tanish[patient_id %in% tanish_predictions[patient_CI == 1 & AD_Med_or_ICD_Code == 0,patient_id]])



## read in gold standards 
# gold <- fread("data/Dementia_ReferenceStandardDataset_08292019_subset_mrn.csv")
# gold[,Label := ifelse(syndromic_dx %in% c(1,2,3,4,9),1,0)]
# structured_variables[gold,on= .(EMPI = empi),Label := i.syndromic_dx]
# 
# test_set_EMPIs <- fread('test_empi_0.csv')
# test_set <- structured_variables[EMPI %in% test_set_EMPIs$EMPI]
# structured_variables <- structured_variables[!EMPI %in% test_set_EMPIs$EMPI] 
# train_set_EMPIs <- fread('train_empi_0.csv')
# structured_variables <- structured_variables[EMPI %in% train_set_EMPIs$EMPI] 
# 
# structured_variables[,.N,by = .(Label)]
# structured_variables[,EMPI := NULL]
# test_set <- test_set[,.(Dx_Count,Med_Count,Label,EMPI)]
# structured_variables[,Label := ifelse(Label %in% c(1,2,3,4,9),1,0)]
# test_set[,Label := ifelse(Label %in% c(1,2,3,4,9),1,0)]


