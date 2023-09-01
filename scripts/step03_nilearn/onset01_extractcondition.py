#!/usr/bin/env python
"""convert behavioral file into event lists and singletrial format

- regressor of interest per task
- duration of epoch
- rating onset
- potential covariates?
"""

# %%
import numpy as np
import pandas as pd
import os, glob, re
from os.path import join
from pathlib import Path
__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Heejung"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development" 

# %% -----------------------------------------------
#                       saxe
# -------------------------------------------------

# * add argparse: sub, 
# * add directories: main_dir, beh_dir, fmri_dir
# * get onset by subtracting trigger
# * get epoch of interest: 
# 'event02_filetype', 'event02_story_onset',
# 'event03_question_onset', 'event04_response_onset',
# 'event04_RT','accuracy'

# sub = 'sub-0009'
# ses = 'ses-04'
task_name = "tomsaxe"
current_path = Path.cwd()
main_dir = current_path.parent.parent #'/Users/h/Documents/projects_local/spacetop_fractional_analysis'
beh_inputdir = join(main_dir, 'data', 'beh', 'beh02_preproc')

saxe_flist = glob.glob(join(beh_inputdir, '**', f'*{task_name}*.csv'), recursive=True)
for saxe_fpath in sorted(saxe_flist):
    saxe_fname = os.path.basename(saxe_fpath)
    sub_bids = re.search(r'sub-\d+', saxe_fname).group(0)
    ses_bids = re.search(r'ses-\d+', saxe_fname).group(0)
    run_bids = re.search(r'run-\d+', saxe_fname).group(0)
    task_name = re.search(r'run-\d+-(\w+)_beh', saxe_fname).group(1)
        # beh_fpath = join(beh_inputdir, sub, f"{sub}_{ses}_task-fractional_{run_bids}-tomsaxe_beh.csv")
    beh_df = pd.read_csv(saxe_fpath)
    subset_beh = beh_df[['event02_filetype', 'event02_story_onset','event03_question_onset', 'event04_response_onset','event04_RT','accuracy']]

    # belief, photo, rating, accuracy as covariate
    subset_belief = pd.DataFrame(); subset_photo = pd.DataFrame(); subset_rating = pd.DataFrame(); 

    subset_belief['onset'] = subset_beh.loc[subset_beh.event02_filetype == 'false_belief', 'event02_story_onset']
    subset_belief['duration'] = 11
    subset_belief['trial_type'] = 'false_belief'
    subset_belief['pmod_accuracy'] = subset_beh.loc[subset_beh.event02_filetype == 'false_belief', 'accuracy']

    subset_photo['onset'] = subset_beh.loc[subset_beh.event02_filetype == 'false_photo', 'event02_story_onset']
    subset_photo['duration'] = 11
    subset_photo['trial_type'] = 'false_photo'
    subset_photo['pmod_accuracy'] = subset_beh.loc[subset_beh.event02_filetype == 'false_photo', 'accuracy']

    subset_rating['onset'] = subset_beh.event03_question_onset
    subset_rating['duration'] = subset_beh.event04_RT
    subset_rating['trial_type'] = 'rating' #'rating_' + subset_beh['event02_filetype'].str.replace('_', '')
    subset_rating['pmod_accuracy'] = subset_beh.accuracy #'rating_' + subset_beh['event02_filetype'].str.replace('_', '')

    # concatenate above dataframes and save in new folder
    events = pd.concat([subset_belief, subset_photo, subset_rating], ignore_index=True)
    
    beh_savedir = join(main_dir, 'data' , 'beh', 'beh03_bids', sub_bids)
    Path(beh_savedir).mkdir( parents=True, exist_ok=True )
    # extract bids info and save as new file
    events.to_csv(join(beh_savedir, f"{sub_bids}_{ses_bids}_task-{task_name}_{run_bids}_events.tsv"), sep='\t', index=False)



# %%
# %% -----------------------------------------------
#                       posner
# -------------------------------------------------
task_name = "posner"
current_path = Path.cwd()
main_dir = current_path.parent.parent #'/Users/h/Documents/projects_local/spacetop_fractional_analysis'
beh_inputdir = join(main_dir, 'data', 'beh', 'beh02_preproc')

posner_flist = glob.glob(join(beh_inputdir, '**', f'*{task_name}*.csv'), recursive=True)
# %%
for posner_fpath in sorted(posner_flist):
    posner_fname = os.path.basename(posner_fpath)
    sub_bids = re.search(r'sub-\d+', posner_fname).group(0)
    ses_bids = re.search(r'ses-\d+', posner_fname).group(0)
    run_bids = re.search(r'run-\d+', posner_fname).group(0)
    task_name = re.search(r'run-\d+-(\w+)_beh', posner_fname).group(1)
    print(f"{sub_bids} {ses_bids} {run_bids} {task_name}")
        # beh_fpath = join(beh_inputdir, sub, f"{sub}_{ses}_task-fractional_{run_bids}-tomsaxe_beh.csv")
    beh_df = pd.read_csv(posner_fpath)
    subset_beh = beh_df[['param_valid_type', 'event02_cue_onset','event03_target_onset', 'event04_response_onset','event04_RT','accuracy']]

    # belief, photo, rating, accuracy as covariate
    subset_valid = pd.DataFrame(); subset_invalid = pd.DataFrame(); subset_target = pd.DataFrame(); 

    subset_valid['onset'] = subset_beh.loc[subset_beh.param_valid_type == 'valid', 'event02_cue_onset']
    subset_valid['duration'] = 0.2
    subset_valid['trial_type'] = 'cue_valid'
    subset_valid['pmod_accuracy'] = subset_beh.loc[subset_beh.param_valid_type == 'valid', 'accuracy']

    subset_invalid['onset'] = subset_beh.loc[subset_beh.param_valid_type == 'invalid', 'event02_cue_onset']
    subset_invalid['duration'] = 0.2
    subset_invalid['trial_type'] = 'cue_invalid'
    subset_invalid['pmod_accuracy'] = subset_beh.loc[subset_beh.param_valid_type == 'invalid', 'accuracy']

    subset_target['onset'] = subset_beh.event03_target_onset
    subset_target['duration'] = subset_beh.event04_RT
    subset_target['trial_type'] = 'target_response' #'rating_' + subset_beh['event02_filetype'].str.replace('_', '')
    subset_target['pmod_accuracy'] = subset_beh.accuracy #'rating_' + subset_beh['event02_filetype'].str.replace('_', '')

    # concatenate above dataframes and save in new folder
    events = pd.concat([subset_valid, subset_invalid, subset_target], ignore_index=True)

    beh_savedir = join(main_dir, 'data' , 'beh', 'beh03_bids', sub_bids)
    Path(beh_savedir).mkdir( parents=True, exist_ok=True )
    # extract bids info and save as new file
    events.to_csv(join(beh_savedir, f"{sub_bids}_{ses_bids}_task-{task_name}_{run_bids}_events.tsv"), sep='\t', index=False)

# %% -----------------------------------------------
#                       posner 2
# -------------------------------------------------
task_name = "posner"
current_path = Path.cwd()
main_dir = current_path.parent.parent #'/Users/h/Documents/projects_local/spacetop_fractional_analysis'
beh_inputdir = join(main_dir, 'data', 'beh', 'beh02_preproc')

posner_flist = glob.glob(join(beh_inputdir, '**', f'*{task_name}*.csv'), recursive=True)
# %%
for posner_fpath in sorted(posner_flist):
    posner_fname = os.path.basename(posner_fpath)
    sub_bids = re.search(r'sub-\d+', posner_fname).group(0)
    ses_bids = re.search(r'ses-\d+', posner_fname).group(0)
    run_bids = re.search(r'run-\d+', posner_fname).group(0)
    task_name = re.search(r'run-\d+-(\w+)_beh', posner_fname).group(1)
    print(f"{sub_bids} {ses_bids} {run_bids} {task_name}")
        # beh_fpath = join(beh_inputdir, sub, f"{sub}_{ses}_task-fractional_{run_bids}-tomsaxe_beh.csv")
    beh_df = pd.read_csv(posner_fpath)
    subset_beh = beh_df[['param_valid_type', 'event02_cue_onset','event03_target_onset', 'event04_response_onset','event04_RT','accuracy']]

    # belief, photo, rating, accuracy as covariate
    subset_valid = pd.DataFrame(); subset_invalid = pd.DataFrame(); subset_target = pd.DataFrame(); 

    subset_valid['onset'] = subset_beh.loc[subset_beh.param_valid_type == 'valid', 'event02_cue_onset']
    subset_valid['duration'] = 0.2 + subset_beh.loc[subset_beh.param_valid_type == 'valid', 'event04_RT']
    subset_valid['trial_type'] = 'cue_valid'
    subset_valid['pmod_accuracy'] = subset_beh.loc[subset_beh.param_valid_type == 'valid', 'accuracy']

    subset_invalid['onset'] = subset_beh.loc[subset_beh.param_valid_type == 'invalid', 'event02_cue_onset']
    subset_invalid['duration'] = 0.2 + subset_beh.loc[subset_beh.param_valid_type == 'invalid', 'event04_RT']
    subset_invalid['trial_type'] = 'cue_invalid'
    subset_invalid['pmod_accuracy'] = subset_beh.loc[subset_beh.param_valid_type == 'invalid', 'accuracy']

    # subset_target['onset'] = subset_beh.event03_target_onset
    # subset_target['duration'] = subset_beh.event04_RT
    # subset_target['trial_type'] = 'target_response' #'rating_' + subset_beh['event02_filetype'].str.replace('_', '')
    # subset_target['pmod_accuracy'] = subset_beh.accuracy #'rating_' + subset_beh['event02_filetype'].str.replace('_', '')

    # concatenate above dataframes and save in new folder
    events = pd.concat([subset_valid, subset_invalid, subset_target], ignore_index=True)

    beh_savedir = join(main_dir, 'data' , 'beh', 'beh03_bids', sub_bids)
    Path(beh_savedir).mkdir( parents=True, exist_ok=True )
    # extract bids info and save as new file
    events.to_csv(join(beh_savedir, f"{sub_bids}_{ses_bids}_task-{task_name}_{run_bids}_events.tsv"), sep='\t', index=False)



# %% -----------------------------------------------
#                      memory
# -------------------------------------------------
"""
<< memory_beh.csv >>
    * extract trigger onset 
    * (we'll use this to subtract from all onsets)

<< study01_beh.csv >>
trial_type: 
    * study_dummy (event02_dummy_stimuli_type)
    * 'study' (event02_dummy_stimuli_type)
image_fname
    * [event02_image_filename]
onset:
    * [RAW_event02_image_onset] [event02_image_onset]
duration
    * [RAW_event03_isi_onset] - [RAW_event02_image_onset]

<< test01_beh.csv >>
trial_type
    * 'test'
image_fname
    * [event02_image_filename]
onset
    * [event02_image_onset]
duration
    * [event03_RT]
pmod_accuracy
    * [event03_response_key] (fill NA with 0)
    * compare with [param_answer]

"""
task_name = "memory"
current_path = Path.cwd()
main_dir = current_path.parent.parent #
main_dir = '/Users/h/Documents/projects_local/spacetop_fractional_analysis'
beh_inputdir = join(main_dir, 'data', 'beh', 'beh02_preproc')

# memory_flist = glob.glob(join(beh_inputdir, '**', f'*{task_name}*.csv'), recursive=True)
memory_flist = sorted(glob.glob(join(beh_inputdir, '**', f'*{task_name}_beh.csv'), recursive=True))

for memory_fpath in memory_flist:
    memory_fname = os.path.basename(memory_fpath)
    sub_bids = re.search(r'sub-\d+', memory_fname).group(0)
    ses_bids = re.search(r'ses-\d+', memory_fname).group(0)
    run_bids = re.search(r'run-\d+', memory_fname).group(0)
    task_name = re.search(r'run-\d+-(\w+)_beh', memory_fname).group(1)
    print(f"{sub_bids} {ses_bids} {run_bids} {task_name}")
    membids_df = pd.DataFrame(columns=['onset', 'duration', 'trial_type', 'pmod_accuracy', 'image_fname'])

    df_memmain = pd.read_csv(memory_fpath)
    trigger = df_memmain['param_trigger_onset'].values[0]

    # -> << study >>
    memory_study_flist = sorted(glob.glob(join(beh_inputdir, sub_bids, f'{sub_bids}_ses-04_task-fractional_{run_bids}_memory_study*_beh.csv' )))
    for memory_study_fname in memory_study_flist:
        print(os.path.basename(memory_study_fname))
        df_memstudy = pd.read_csv(memory_study_fname)
        temp_study = pd.DataFrame(columns=['onset', 'duration', 'trial_type', 'pmod_accuracy', 'image_fname']) #.append(pd.DataFrame(index=range(df_memstudy01.shape[0])))
        temp_study['trial_type'] = df_memstudy['event02_dummy_stimuli_type'].replace({0: 'dummy', 1: 'study'})
        temp_study['onset'] = df_memstudy['RAW_event02_image_onset'] - trigger
        temp_study['duration'] = df_memstudy['RAW_event03_isi_onset'] - df_memstudy['RAW_event02_image_onset']
        temp_study['image_fname'] = df_memstudy['event02_image_filename']
        temp_study['pmod_accuracy'] = np.nan
        membids_df = pd.concat([membids_df, temp_study], ignore_index=True)

    # -> test onset
    memory_test_flist = sorted(glob.glob(join(beh_inputdir, sub_bids, f'{sub_bids}_ses-04_task-fractional_{run_bids}_memory_test*_beh.csv' )))
    for memory_test_fname in memory_test_flist:
        print(os.path.basename(memory_test_fname))
        df_memtest = pd.read_csv(memory_test_fname)
        temp_test = pd.DataFrame(columns=['onset', 'duration', 'trial_type', 'pmod_accuracy', 'image_fname']) #.append(pd.DataFrame(index=range(df_memstudy01.shape[0])))
        temp_test['onset'] = df_memtest['RAW_event02_image_onset'] - trigger
        temp_test['duration'] = df_memtest['RAW_event03_response_onset'] - df_memtest['RAW_event02_image_onset']
        temp_test['duration'] = temp_test['duration'].fillna(2) # if duration is na, fill with 2
        temp_test['image_fname'] = df_memtest['event02_image_filename']
        df_memtest['event03_response_key'] = df_memtest['event03_response_key'].fillna(0)
        temp_test['pmod_accuracy'] = (df_memtest['param_answer'] == df_memtest['event03_response_key']).astype(int)
        temp_test['trial_type'] = 'test'
        membids_df = pd.concat([membids_df, temp_test], ignore_index=True)

    # -> test onset
    memory_dist_flist = sorted(glob.glob(join(beh_inputdir, sub_bids, f'{sub_bids}_ses-04_task-fractional_{run_bids}_memory_distraction*_beh.csv' )))
    for memory_dist_fname in memory_dist_flist:
        print(os.path.basename(memory_dist_fname))
        df_memdist = pd.read_csv(memory_dist_fname)
        temp_dist = pd.DataFrame(columns=['onset', 'duration', 'trial_type', 'pmod_accuracy', 'image_fname']) #.append(pd.DataFrame(index=range(df_memstudy01.shape[0])))
        temp_dist['onset'] = df_memdist['p2_operation'] - trigger
        temp_dist['duration'] = 25 #df_memdist['p5_fixation_onset'] - df_memdist['p2_operation']
        temp_dist['image_fname'] = np.nan
        temp_dist['pmod_accuracy'] = np.nan
        temp_dist['trial_type'] = 'math'
        membids_df = pd.concat([membids_df, temp_dist], ignore_index=True)
    
    beh_savedir = join(main_dir, 'data' , 'beh', 'beh03_bids', sub_bids)
    Path(beh_savedir).mkdir( parents=True, exist_ok=True )
    save_fname = f"{sub_bids}_ses-04_task-{task_name}_{run_bids}_events.tsv"
    membids_df.to_csv(join(beh_savedir, save_fname), sep='\t', index=False)





# %% -----------------------------------------------
#                       spunt
# -------------------------------------------------
"""
[param_cond_type_string]: c4_HowHand
[param_normative_response]: correct answer
[param_image_filename]: image_fname
param_trigger_onset
onset: [event02_image_onset] [RAW_e2_image_onset] - param_trigger_onset
duration: [event02_image_dur] [RAW_e3_response_onset] - [RAW_e2_image_onset] 
trial_type:
button_press: [RAW_e3_response_onset] - [param_trigger_onset]
pmod_accuracy: [accuracy]

param_normative_response: 1, 2
event03_response_key: 1,3 -> convert to 1,2
"""
task_name = "tomspunt"
current_path = Path.cwd()
main_dir = current_path.parent.parent #
main_dir = '/Users/h/Documents/projects_local/spacetop_fractional_analysis'
beh_inputdir = join(main_dir, 'data', 'beh', 'beh02_preproc')

# memory_flist = glob.glob(join(beh_inputdir, '**', f'*{task_name}*.csv'), recursive=True)
spunt_flist = sorted(glob.glob(join(beh_inputdir, '**', f'*{task_name}_beh.csv'), recursive=True))
for spunt_fpath in spunt_flist:
    spunt_fname = os.path.basename(spunt_fpath)
    sub_bids = re.search(r'sub-\d+', spunt_fname).group(0)
    ses_bids = re.search(r'ses-\d+', spunt_fname).group(0)
    run_bids = re.search(r'run-\d+', spunt_fname).group(0)
    task_name = re.search(r'run-\d+-(\w+)_beh', spunt_fname).group(1)
    print(f"{sub_bids} {ses_bids} {run_bids} {task_name}")
    df_spunt = pd.read_csv(spunt_fpath)

    events = pd.DataFrame(columns=['onset', 'duration', 'trial_type', 'pmod_accuracy', 'image_fname']) 
    button = pd.DataFrame(columns=['onset', 'duration', 'trial_type', 'pmod_accuracy', 'image_fname']) 
    events['onset'] = df_spunt['RAW_e2_image_onset'] - df_spunt['param_trigger_onset']
    events['duration'] = df_spunt['RAW_e3_response_onset'] - df_spunt['RAW_e2_image_onset'] 
    df_spunt['trial_type'] = df_spunt['param_cond_type_string'].str.replace('^(c[1234])_', '', regex=True).str.replace(r'([a-z])([A-Z])', r'\1_\2').str.lower()
    events['trial_type'] = df_spunt['trial_type'].str[:3] + '_' + df_spunt['trial_type'].str[3:]
    events['image_fname'] = df_spunt['param_image_filename']


    df_spunt['reponse_subject'] = df_spunt['event03_response_key'].replace(3, 2)
    events['pmod_accuracy'] = (df_spunt['param_normative_response'] == df_spunt['reponse_subject']).astype(int)

    button['onset'] = df_spunt['RAW_e3_response_onset'] - df_spunt['param_trigger_onset']
    button['duration'] = 1
    button['trial_type'] = 'buttonpress'
    button['image_fname'] = df_spunt['param_image_filename']
    button['pmod_accuracy'] = np.nan

    events = pd.concat([events, button], ignore_index=True)

    beh_savedir = join(main_dir, 'data' , 'beh', 'beh03_bids', sub_bids)
    Path(beh_savedir).mkdir( parents=True, exist_ok=True )
    save_fname = f"{sub_bids}_ses-04_task-{task_name}_{run_bids}_events.tsv"
    events.to_csv(join(beh_savedir, save_fname), sep='\t', index=False)
# Print the updated DataFrame

# %%
