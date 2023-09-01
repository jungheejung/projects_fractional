#!/usr/bin/env python
"""Builds a glm based on memory task

Events of interest:
- encoding items
- test old
- test new

manipulation check: rating
contrast of interest: test old vs test new
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
from nilearn.glm import threshold_stats_img
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

# %% ---------------------------------
#          local parameters
# ------------------------------------


# main_dir = '/Users/h/Documents/projects_local/spacetop_fractional_analysis'
# fmriprep_dir = '/Users/h/Documents/projects_local/sandbox/fmriprep_bold'
current_path = Path.cwd()
main_dir = current_path.parent.parent #'/Users/h/Documents/projects_local/spacetop_fractional_analysis'
beh_dir = join(main_dir, 'data' , 'beh', 'beh03_bids')

#   -> glob behavioral file 
mem_flist = glob.glob(join(beh_dir, '**', f'*{task_name}*.tsv'), recursive=True)
print(main_dir)
print(mem_flist)
mem_behfpath = mem_flist[slurm_id]
mem_behfname = os.path.basename(mem_behfpath)

# sub = 'sub-0010'
# ses = 'ses-04'
# run_num = 2
# task_name = 'memory'
# mem_behfpath = '/Users/h/Documents/projects_local/spacetop_fractional_analysis/data/beh/beh03_bids/sub-0010/sub-0010_ses-04_task-memory_run-01_events.tsv'
#   -> extract sub, ses, task , run 
sub = re.search(r'sub-\d+', mem_behfname).group(0)
ses = re.search(r'ses-\d+', mem_behfname).group(0)
run = re.search(r'run-\d+', mem_behfname).group(0)
run_num = int(re.search(r'run-(\d+)', mem_behfname).group(1))

#   -> glm output dir
glm_savedir = join(main_dir, 'analysis', 'fmri', 'nilearn', 'glm', f'task-{task_name}', sub)
Path(glm_savedir).mkdir( parents=True, exist_ok=True )

# %% ---------------------------------
#     load beh, fmri, confound data
# ------------------------------------
#   -> load events.tsv:
events_fname = mem_behfpath #join(beh_dir, f"{sub}_{ses}_task-{task_name}_{run}_events.tsv")
events = pd.read_csv(events_fname, sep = '\t')
print(f"events_fname: {events_fname}")
#   -> load brain img:
fmri_img = nilearn.image.load_img(join(fmriprep_dir, sub, ses, 'func', f'{sub}_ses-04_task-fractional_acq-mb8_run-{run_num}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'))
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
    #  'memory': Memory(location=None),
    #  'memory_level': 1,
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

#inspect the design matrix 
design_matrix = fmri_glm.design_matrices_[0]

plotting.plot_design_matrix(design_matrix, 
                            output_file=join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_designmatrix.png"))
plt.close()

plt.plot(design_matrix["study"]); plt.xlabel("scan"); plt.title("study conditions")
plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_event-study_boldsignal.png")) 
plt.close() 

plt.plot(design_matrix["test"]); plt.xlabel("scan"); plt.title("test conditions")
plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_event-test_boldsignal.png")) 
plt.close() 

# %% ---------------------------------
#           contrasts
# ------------------------------------
# %% Detecting voxels with significant effects _______________
conditions = {"dummy": np.zeros(design_matrix.shape[1]),
              "math": np.zeros(design_matrix.shape[1]),
              "study": np.zeros(design_matrix.shape[1]), 
              "test": np.zeros(design_matrix.shape[1]),
              }
conditions["dummy"][0] = 1
conditions["math"][1] = 1
conditions["study"][[0,2]] = 1
conditions["test"][3] = 1


study_gt_test = conditions["study"] - conditions["test"]
study_gt_math = conditions["study"] - conditions["math"]
test_gt_math = conditions["test"] - conditions["math"]

plotting.plot_contrast_matrix(study_gt_test, design_matrix=design_matrix)
plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-01_desc-studyGTtest.png")) 
plt.close()

plotting.plot_contrast_matrix(study_gt_math, design_matrix=design_matrix)
plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-02_desc-studyGTmath.png")) 
plt.close()

plotting.plot_contrast_matrix(test_gt_math, design_matrix=design_matrix)
plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-03_desc-testGTmath.png")) 
plt.close()

# effect size map and Z-maps __________________
beta_study_gt_test = fmri_glm.compute_contrast(study_gt_test, output_type="effect_size")
beta_study_gt_math = fmri_glm.compute_contrast(study_gt_math, output_type="effect_size")
beta_test_gt_math  = fmri_glm.compute_contrast(test_gt_math, output_type="effect_size")

Z_study_gt_test = fmri_glm.compute_contrast(study_gt_test, output_type="z_score")
Z_study_gt_math = fmri_glm.compute_contrast(study_gt_math, output_type="z_score")
Z_test_gt_math  = fmri_glm.compute_contrast(test_gt_math, output_type="z_score")

plotting.plot_stat_map(
    Z_study_gt_test,
    bg_img=image.mean_img(fmri_img),
    threshold=3.0,
    cut_coords=5,
    display_mode='mosaic',
    black_bg=True,
    title="encode > retrieval (Z > 3)",
)
plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-01_desc-encodeGTretrieval_stat-zmap.png")) 
plt.close() 

plotting.plot_stat_map(
    Z_study_gt_math,
    bg_img=image.mean_img(fmri_img),
    threshold=3.0,
    cut_coords=5,
    display_mode='mosaic',
    black_bg=True,
    title="encode > retrieval (Z > 3)",
)
plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-02_desc-encodeGTmath_stat-zmap.png")) 
plt.close() 

plotting.plot_stat_map(
    Z_test_gt_math,
    bg_img=image.mean_img(fmri_img),
    threshold=3.0,
    cut_coords=5,
    display_mode='mosaic',
    black_bg=True,
    title="encode > retrieval (Z > 3)",
)
plt.savefig(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-03_desc-retrievalGTmath_stat-zmap.png")) 
plt.close() 
# %% ---------------------------------
#         save outputs
# ------------------------------------
beta_study_gt_test.to_filename(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-01_desc-encodeGTretrieval_stat-betamap.nii.gz"))
beta_study_gt_math.to_filename(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-02_desc-encodeGTmath_stat-betamap.nii.gz"))
beta_test_gt_math.to_filename(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-03_desc-retrievalGTmath_stat-betamap.nii.gz"))


Z_study_gt_test.to_filename(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-01_desc-encodeGTretrieval_stat-zmap.nii.gz"))
Z_study_gt_math.to_filename(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-02_desc-encodeGTmath-zmap.nii.gz"))
Z_test_gt_math.to_filename(join(glm_savedir, f"{sub}_{ses}_task-{task_name}_run-{run_num:02d}_con-03_desc-retrievalGTmath-zmap.nii.gz"))

# %%
