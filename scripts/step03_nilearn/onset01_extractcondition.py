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
current_path = Path.cwd()
main_dir = current_path.parent.parent #'/Users/h/Documents/projects_local/spacetop_fractional_analysis'
beh_inputdir = join(main_dir, 'data', 'beh', 'beh02_preproc')

saxe_flist = glob.glob(join(beh_inputdir, '**', '*tomsaxe*.csv'), recursive=True)
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
