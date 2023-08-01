#!/usr/bin/env python
"""Builds a glm based on the posner task

Events of interest:
- cue (valid vs. invalid)
- target targetresponse (target phase is non-separable from the button press phase)

manipulation check: targetresponse
contrast of interest: valid vs invalid cue
"""
# %%
import numpy as np
import pandas as pd
import os, glob, re
from os.path import join
from pathlib import Path
import nilearn
import argparse
from nilearn import image, plotting
from nilearn.glm.first_level import FirstLevelModel
import matplotlib.pyplot as plt

__author__ = "Heejung Jung"
__copyright__ = "Spatial Topology Project"
__credits__ = ["Heejung"] # people who reported bug fixes, made suggestions, etc. but did not actually write the code.
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Heejung Jung"
__email__ = "heejung.jung@colorado.edu"
__status__ = "Development" 

# %% ---------------------------------
#           parameters
# ------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--slurm-id", type=int,
                    help="specify slurm array id")
parser.add_argument("--task", type=str,
                    help="taskname")
parser.add_argument("--fmriprep-dir", type=str,
                    help="filepath where fmriprep preprocessed files are")
args = parser.parse_args()
slurm_id = args.slurm_id
task_name = args.task
fmriprep_dir = args.fmriprep_dir

current_path = Path.cwd()
main_dir = current_path.parent.parent #'/Users/h/Documents/projects_local/spacetop_fractional_analysis'
beh_dir = join(main_dir, 'data' , 'beh', 'beh03_bids')

# -> glob behavioral file 
posner_flist = glob.glob(join(beh_dir, '**', f'*{task_name}*.tsv'), recursive=True)
posner_behfpath = posner_flist[slurm_id]
posner_behfname = os.path.basename(posner_behfpath)

# -> extract sub, ses, task , run 
sub = re.search(r'sub-\d+', posner_behfname).group(0)
ses = re.search(r'ses-\d+', posner_behfname).group(0)
run = re.search(r'run-\d+', posner_behfname).group(0)
run_num = int(re.search(r'run-(\d+)', posner_behfname).group(1))

glm_savedir = join(main_dir, 'analysis', 'fmri', 'nilearn', 'glm', f'task-{task_name}', sub)
Path(glm_savedir).mkdir( parents=True, exist_ok=True )


# %% ---------------------------------
#     local sandbox
# ------------------------------------
sub = "sub-0009"
ses = "ses-04"
run_num = 1
fmriprep_dir = '/Users/h/Documents/projects_local/sandbox'
events_fname = '/Users/h/Documents/projects_local/spacetop_fractional_analysis/data/beh/beh03_bids/sub-0009/sub-0009_ses-04_task-posner_run-01_events.tsv'
glm_savedir = '/Users/h/Documents/projects_local/sandbox'
posner_behfpath = '/Volumes/spacetop_projects_fractional/data/beh/beh03_bids/sub-0009/sub-0009_ses-04_task-posner_run-01_events.tsv'
# %% ---------------------------------
#     load beh, fmri, confound data
# ------------------------------------
#   -> load events.tsv:
# events_fname = posner_behfpath #join(beh_dir, f"{sub}_{ses}_task-{task_name}_{run}_events.tsv")
events = pd.read_csv(posner_behfpath, sep = '\t')
#   -> load brain img:
fmri_img = nilearn.image.load_img(join(fmriprep_dir, sub, 'ses-04', 'func', f'{sub}_ses-04_task-fractional_acq-mb8_run-{run_num}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'))
#   -> nuissance cov  
confounds_file = os.path.join(fmriprep_dir, sub, ses, 'func', f'{sub}_{ses}_task-fractional_acq-mb8_run-{run_num}_desc-confounds_timeseries.tsv')
confounds = pd.read_csv(confounds_file, sep = '\t')
filter_col = [col for col in confounds if col.startswith('motion')]
default_csf_24dof = ['csf', 'trans_x', 'trans_x_derivative1', 'trans_x_power2', 'trans_x_derivative1_power2',
                            'trans_y', 'trans_y_derivative1', 'trans_y_derivative1_power2', 'trans_y_power2',
                            'trans_z', 'trans_z_derivative1', 'trans_z_derivative1_power2', 'trans_z_power2',
                            'rot_x', 'rot_x_derivative1', 'rot_x_derivative1_power2', 'rot_x_power2', 
                            'rot_y', 'rot_y_derivative1', 'rot_y_derivative1_power2', 'rot_y_power2', 
                            'rot_z', 'rot_z_derivative1', 'rot_z_derivative1_power2', 'rot_z_power2']
filter_col.extend(default_csf_24dof)
dummy = pd.DataFrame(np.eye(len(confounds))).loc[:,0:5]
dummy.rename(columns = {0:'dummy_00',
                    1:'dummy_01',
                    2:'dummy_02',3:'dummy_03',4:'dummy_04',5:'dummy_05'}, inplace=True)
subset_confounds = pd.concat([confounds[filter_col], dummy], axis = 1)
print("grabbed all the confounds and fmri data")
subset_confounds.head()

# %% ---------------------------------
#           glm building
# ------------------------------------
glm_parameters = {'drift_model':None,
    'drift_order': 1,
    'fir_delays': [0],
    'high_pass': 0.01, #This parameter specifies the cut frequency of the high-pass filter in Hz for the design matrices. Used only if drift_model is ‘cosine’. Default=0.01.
    'hrf_model': 'spm', #
    'mask_img': None,
    'min_onset': -24,
    'minimize_memory': True,
    'n_jobs': 1,
    'noise_model': 'ols', #'ar1',
    'random_state': None,
    'signal_scaling': 0,
    'slice_time_ref': 0.0,
    'smoothing_fwhm': None,
    'standardize': False, #
    'subject_label': '01', # 
    't_r': 0.46, #
    'target_affine': None, #
    'target_shape': None, #
    'verbose': 0}

fmri_glm = FirstLevelModel(**glm_parameters)
fmri_glm = fmri_glm.fit(fmri_img, 
                        events=events, 
                        confounds=subset_confounds.fillna(0))
# -> inspect the design matrix 
design_matrix = fmri_glm.design_matrices_[0]

plotting.plot_design_matrix(design_matrix, 
                            output_file=join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_designmatrix.png"))
plt.close()

plt.plot(design_matrix["cue_valid"]); plt.xlabel("scan"); plt.title("valid cue conditions")
plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_boldsignal.png")) 
plt.close() 


# %% ---------------------------------
#           contrasts
# ------------------------------------
# -> Detecting voxels with significant effects _______________
conditions = {"cue_invalid": np.zeros(design_matrix.shape[1]), 
              "cue_valid": np.zeros(design_matrix.shape[1])}
            #   "target_response": np.zeros(design_matrix.shape[1])}
conditions["cue_invalid"][0] = 1
conditions["cue_valid"][1] = 1
# conditions["target_response"][2] = 1

# #####
events[events['trial_type'] == 'target_response']

invalid_gt_valid = conditions["cue_invalid"] - conditions["cue_valid"]
# targetresponse = conditions["target_response"]
plotting.plot_contrast_matrix(invalid_gt_valid, design_matrix=design_matrix)
plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-01_desc-invalidGTvalid.png")) 
plt.close()
# plotting.plot_contrast_matrix(targetresponse, design_matrix=design_matrix)
# plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-02_desc-targetresponse.png")) 
# plt.close() 

# -> effect size map and Z-maps __________________
beta_invalid_gt_valid = fmri_glm.compute_contrast(invalid_gt_valid, output_type="effect_size")
# beta_targetresponse = fmri_glm.compute_contrast(targetresponse, output_type="effect_size")
Z_invalid_gt_valid = fmri_glm.compute_contrast(invalid_gt_valid, output_type="z_score")
# Z_targetresponse = fmri_glm.compute_contrast(targetresponse, output_type="z_score")

plotting.plot_stat_map(
    Z_invalid_gt_valid,
    bg_img=image.mean_img(fmri_img),
    threshold=3.0,
    cut_coords=5,
    display_mode='mosaic',
    black_bg=True,
    title="Invalid > Valid (Z > 3)",
)
plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-01_desc-invalidGTvalid_stat-zmap.png")) 
plt.close() 

# plotting.plot_stat_map(
#     Z_targetresponse,
#     bg_img=image.mean_img(fmri_img),
#     threshold=3.0,
#     cut_coords=5,
#     display_mode='mosaic',
#     black_bg=True,
#     title="targetresponse motor respose (Z > 3)",
# )
# plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-02_desc-targetresponse_stat-zmap.png")) 
# plt.close()
# %% ---------------------------------
#         save outputs
# ------------------------------------
beta_invalid_gt_valid.to_filename(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-01_desc-invalidGTvalid_stat-betamap.nii.gz"))
# beta_targetresponse.to_filename(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-02_desc-targetresponse_stat-betamap.nii.gz"))

Z_invalid_gt_valid.to_filename(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-01_desc-invalidGTvalid_stat-zmap.nii.gz"))
# Z_targetresponse.to_filename(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-02_desc-targetresponse_stat-zmap.nii.gz"))


print(f"---------------:+: COMPLETE :+:------------------")
