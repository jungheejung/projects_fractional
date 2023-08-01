#!/bin/bash -l
#SBATCH --job-name=posner
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=00:30:00
#SBATCH -o ./logposner/np_%A_%a.o
#SBATCH -e ./logposner/np_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-133%10

conda activate spacetop_env
echo "SLURMSARRAY: " ${SLURM_ARRAY_TASK_ID}
ID=$((SLURM_ARRAY_TASK_ID-1))
MAINDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_fractional'
FMRIPREPDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep'
# OUTPUTDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep_qc/numpy_bold'
python ${MAINDIR}/scripts/step03_nilearn/nilearn01_glm_posner_block.py \
--slurm-id ${ID} \
--task "posner" \
--fmriprep-dir ${FMRIPREPDIR} \
# --outputdir ${OUTPUTDIR}
