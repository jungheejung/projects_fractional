import os
import shutil
import glob, re

# Define the source and destination directories
source_dir = '/home/spacetop/repos/fractional/task-memory/data/'
destination_dir = '/home/spacetop/repos/data/'

# Define the pattern for matching files
run_pattern = 'sub-*_ses-*_task-fractional_run-*_memory_*.csv'

# Loop through all subdirectories matching the pattern
for sub_dir in glob.glob(os.path.join(source_dir, 'sub-*')):
    csv_file = glob.glob(os.path.join(sub_dir, 'beh', run_pattern))[0]
    # for csv_file in glob.glob(os.path.join(sub_dir, 'beh', pattern)):
        # Extract run index from the file name
    run_index = csv_file.split('_run-')[1].split('_')[0]
    sub = re.search(r'sub-\d+', os.path.basename(csv_file)).group(0)
    # Generate the new file name
    distract_flist = sorted(glob.glob(os.path.join(sub_dir, 'beh', f"*_task-memory-distraction-*_beh.csv")))
    for distract_fpath in distract_flist:
        distract_index = int(distract_fpath.split('distraction-')[1].split('_')[0])
        new_fname = os.path.join(destination_dir, sub, 'task-fractional', f"{sub}_ses-04_task-fractional_run-{run_index}_memory_distraction{distract_index:02d}_beh.csv")

    # Create the destination directory if it doesn't exist
    new_dir = os.path.join(destination_dir, sub, 'task-fractional')
    os.makedirs(new_dir, exist_ok=True)

    # Copy the file to the new directory with the modified name
    shutil.copy(distract_fpath, os.path.join(new_dir, new_fname))
