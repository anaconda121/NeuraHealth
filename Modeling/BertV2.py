# base libraries
import numpy as np
import pandas as pd
import regex as re
import itertools
import sklearn.metrics as sk
from functools import reduce

# deep learning libraries
import torch
import transformers
from sklearn.model_selection import train_test_split
from simpletransformers.classification import ClassificationModel, ClassificationArgs

# hyperparameter optimization
import optuna
from optuna.samplers import TPESampler
import optuna.visualization.matplotlib as oviz

# file system manipulation
import os
import shutil
from pathlib import Path
import pickle
import copy

# logging
import logging
import time

# define directories
data_dir = Path("../Data")
results_dir = Path("../Results/")

# set seeds to make computations deterministic
np.random.seed(1234)
torch.manual_seed(1234)

# check CUDA availability
cuda_available = torch.cuda.is_available()
print("Is CUDA available? ", "Yes" if cuda_available else "No")

always_patterns = pd.read_csv("input_optimized.csv") 
manual_review = pd.read_csv(r"C:\Users\MIND_DS\Dropbox (Partners HealthCare)\NLP\Tanish\APOE-SLAT\Modeling\test_and_validation.csv")
manual_review = manual_review[['patient_id', 'sequence', 'annotator_label']]
always_patterns = always_patterns[['patient_id', 'sequence', 'annotator_label']]

def split_data(trial):
    # stratify across sequences with and without always pattern matches and class_label (Y, N, NTR)
    
    # stratifying across sequences with always pattern
    X_train, X_other = train_test_split(always_patterns, random_state = 0,test_size = 0.1, stratify = always_patterns["annotator_label"].to_numpy())

    X_valid, X_test = train_test_split(X_other, random_state = 0, test_size = 0.25, stratify = X_other["annotator_label"].to_numpy())
    
    # stratifying across sequences without always pattern
    X_train_2, X_other_2 = train_test_split(manual_review, random_state = 0,test_size = 0.6, stratify = manual_review["annotator_label"].to_numpy())

    X_valid_2, X_test_2 = train_test_split(X_other_2, random_state = 0, test_size = (0.25/0.6), stratify = X_test_2["annotator_label"].to_numpy())
    
    # combining to get final train, test, validation splits
    X_train = X_train.append(X_train_2)
    X_valid = X_valid.append(X_valid_2)
    X_test = X_test.append(X_test_2)

    return X_train, X_valid, X_test

def define_model(trial, trial_dir):
    # set learning rate
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-1, log = True)

    # define model name
    model_type = "bert"
    model_name = "emilyalsentzer/Bio_ClinicalBERT"
    max_seq_length = 1024

    model_args = ClassificationArgs (
        ## NLP ARGUMENTS
        sliding_window = False,
        learning_rate = learning_rate, # default 4e-5
        adam_epsilon= 1e-8, # default 1e-8
        train_batch_size = 8, # default 8
        eval_batch_size = 4, # default 8
        num_train_epochs = 4,  # default 1 (number of epochs model will be trained for)
        do_lower_case = False, # default False
        max_seq_length = max_seq_length, # default 128 (maximum sequence length the model will support)
        
        ## TRAINING LOOP
        logging_steps = 50, # default 50
        manual_seed = 1234, # default None (necessary for reproducible results)
        n_gpu = 2, # default 1 (number of GPUs to use)
        save_steps = 2000, # default 2000 (save a model checkpoint at every specified number of steps)
        output_dir = trial_dir, 
        overwrite_output_dir = True, # default False (if True, then the trained model will be saved to the ouput_dir and will overwrite existing saved models in the same directory)

        ## EVALUATE DURING TRAINING
        evaluate_during_training = True, # default False
        evaluate_during_training_steps = 2000, # default  2000  
        evaluate_during_training_verbose = True, # default False
        
        ## EARLY STOPPING
        use_early_stopping = True, # default False
        early_stopping_delta = 0, # default 0 (improvement over best_eval_loss necessary to count as a better checkpoint)
        early_stopping_metric = "auc", # default eval_loss 
        early_stopping_metric_minimize = True, # default True
        early_stopping_patience = 3, # default value 3 (terminate training after these many epochs if there is no improvement in early_stopping_metric then early_stopping_delta)
    )

    # create the classification model
    model = ClassificationModel (
        model_type, model_name,
        args = model_args,
        use_cuda = cuda_available
    )
    
    return (model)

def fpr_tpr(df, val):
    thres_list = list(np.arange(0.0, 1.0, 0.01))
    fpr_list = []
    tpr_list = []
    accuracy_list = []

    for thres in thres_list:
        # compare the CB prediction to the threshold of current iteration, convert to binary prediction
        df['PatientLabel'] = df['SeqProbs'].apply(lambda x: 1 if x > thres else 0)
        val[['PatientID', 'labels']].merge(df, on = 'PatientID')

        # calculate TP, FP, TN, FN
        val['TP'] = (val['labels'] == 1) & (val['PatientLabel'] == 1)
        val['TP'] = val['TP'].astype(int)

        val['FP'] = (val['labels'] == 0) & (val['PatientLabel'] == 1)
        val['FP'] = val['FP'].astype(int)

        val['TN'] = (val['labels'] == 0) & (val['PatientLabel'] == 0)
        val['TN'] = val['TN'].astype(int)

        val['FN'] = (val['labels'] == 1) & (val['PatientLabel'] == 0)
        val['FN'] = val['FN'].astype(int)

        tp = sum(val['TP'])
        fp = sum(val['FP'])
        tn = sum(val['TN'])
        fn = sum(val['FN'])

        P = tp + fn
        N = tn + fp
        fpr = fp/N
        tpr = tp/P

        accuracy = (tp+tn)/(P+N)
        fpr_list.append(fpr)
        tpr_list.append(tpr)
        accuracy_list.append(accuracy)
        best_acc_index = accuracy_list.index(max(accuracy_list))
        best_thres = thres_list[best_acc_index]

        return fpr_list, tpr_list, best_thres, val

def CB_scale(df, scaling_factor = 2):
    inputs = df["SeqProbs"]
    return (max(inputs) + (np.average(inputs)*(len(inputs)/scaling_factor)))/(1+(len(inputs)/scaling_factor))

def objective(trial):
    # log time
    start_time = time.localtime()

    # log message
    print("\n-------- TRIAL #{} --------".format(trial.number))

    # create output directory
    trial_dir = "../Results/Model/trial_{}".format(trial.number)
    if os.path.isdir(trial_dir):
        shutil.rmtree(trial_dir)
        print("\n>>> {}: Removing Directory {}\n".format(time.strftime("%H:%M:%S", time.localtime()), trial_dir))
    os.mkdir(trial_dir)

    # log message
    print("\n>>> {}: Preparing Data\n".format(time.strftime("%H:%M:%S", time.localtime())))

    train_data, val_data, test_data = split_data(trial)
    
    # save test dataset to file
    f = open(Path(trial_dir, "data_{}.pkl".format(trial.number)), "wb")
    pickle.dump([train_data, val_data, test_data], f)
    f.close()

    # log message
    print("\n>>> {}: Defining Model\n".format(time.strftime("%H:%M:%S", time.localtime())))

    model = define_model(trial, trial_dir)

    # log message
    print("\n>>> {}: Started Training\n".format(time.strftime("%H:%M:%S", time.localtime())))

    # train model
    model.train_model(
        train_data,
        eval_df = val_data,
        auc = sk.roc_auc_score,
        acc = sk.accuracy_score
    )
    
    results, model_outputs, wrong_predictions = model.eval_model(
        val_data,
        auc = sk.roc_auc_score,
        acc = sk.accuracy_score
    )

    # save to file
    f = open(Path(trial_dir, "training_results_{}.pkl".format(trial.number)), "wb")
    pickle.dump([model, results, model_outputs, wrong_predictions], f)
    f.close()

    # output message, initialize empty list
    print(">>> {}: Get Context Window Probabilities\n".format(time.strftime("%H:%M:%S", time.localtime())))
    df_list = []

    # extract context window probabilities
    for i in range(len(val_data)):
        prob_list = list(torch.softmax(torch.from_numpy(model_outputs[i]), axis=0)[:,1])
        prob_df = pd.DataFrame({
            'SeqProbs': [prob_list],
            'PatientID': val_data.iloc[i]['PatientID'],
            }, columns=['SeqProbs', 'PatientID'])
        # prob_df = pd.DataFrame(prob_list, columns=['SeqProbs'])
        # prob_df['PatientID'] = val_data.iloc[i]['PatientID']
        df_list.append(prob_df)

    # concatenate and save overall window-level probabilities
    cw_probs = pd.concat(df_list, axis=0)
    cw_probs = pd.merge(val_data, cw_probs, how = "right", on = ["PatientID"])
    cw_probs = cw_probs.rename(columns={"text":"Sequence", "labels":"Labels"})
    cw_probs.to_csv(trial_dir + "sequence_probabilities_{}.csv".format(trial.number))

    # group by patient, then apply ClinicalBERT aggregation function
    cw_probs.groupby(["PatientID"]).apply(CB_scale)
    
    # compute metrics
    fpr_ls, tpr_ls, threshold, val_merged = fpr_tpr(cw_probs, val_data)
    best_auc = sk.roc_auc_score(fpr_ls, tpr_ls, average = 'weighted', multi_class = 'ovr')
    
    print(">>> {}: Current AUC: {}\n".format(time.strftime("%H:%M:%S", time.localtime()), best_auc))
    print(">>> {}: Threshold for Validation Accuracy: {}\n".format(time.strftime("%H:%M:%S", time.localtime()), threshold))
    print(">>> {}: Start Training Time\n".format(time.strftime("%H:%M:%S", start_time)))
    print(">>> {}: Finish Training Time\n".format(time.strftime("%H:%M:%S", time.localtime())))

    return(best_auc)

optuna.logging.get_logger("optuna").addHandler(logging.StreamHandler(sys.stdout))

# unique identifier of the study
study_name = "apoe-slat-study" 

# create study database
storage_name = "sqlite:///{}.db".format("../Results/" + study_name)
study = optuna.create_study(direction = "minimize", sampler = TPESampler(seed = 1234, multivariate = True), study_name = study_name, storage = storage_name, load_if_exists = True)
study.optimize(objective, n_trials = 20, gc_after_trial = True)

pruned_trials = [t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED]
complete_trials = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]

print("\nStudy Statistics:")
print("- Finished Trials: ", len(study.trials))
print("- Pruned Trials: ", len(pruned_trials))
print("- Complete Trials: ", len(complete_trials))

print("\nBest Trial:")
best_trial = study.best_trial
print("- Number: ", best_trial.number)
print("- Value: ", best_trial.value)
print("- Hyperparameters: ")
for key, value in best_trial.params.items():
    print("   - {}: {}".format(key, value))
