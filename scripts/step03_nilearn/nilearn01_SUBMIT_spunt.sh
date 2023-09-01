#!/bin/bash -l
#SBATCH --job-name=glmsaxe
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --mem-per-cpu=8gb
#SBATCH --time=01:00:00
#SBATCH -o ./logsaxe/np_%A_%a.o
#SBATCH -e ./logsaxe/np_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --array=1-3%10

conda activate spacetop_env
echo "SLURMSARRAY: " ${SLURM_ARRAY_TASK_ID}
ID=$((SLURM_ARRAY_TASK_ID-1))
MAINDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/spacetop_projects_fractional'
FMRIPREPDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep/results/fmriprep'
# OUTPUTDIR='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/derivatives/fmriprep_qc/numpy_bold'
python ${MAINDIR}/scripts/step03_nilearn/nilearn01_glm_spunt.py \
--slurm-id ${ID} \
--task "spunt" \
--fmriprep-dir ${FMRIPREPDIR} 
# --outputdir ${OUTPUTDIR}
