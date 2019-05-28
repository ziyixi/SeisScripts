#!/bin/bash --login
########## SBATCH Lines for Resource Request ##########
 
#SBATCH --time=06:00:00             # limit of wall clock time - how long the job will run (same as -t)
#SBATCH --ntasks=50                  # number of tasks - how many tasks (nodes) that you require (same as -n)
#SBATCH --mem-per-cpu=8G            # memory required per allocated CPU (or core) - amount of memory (in bytes)
#SBATCH --job-name fnet      # you can give your job a name for easier identification (same as -J)
 
########## Command Lines to Run ##########

# prepare 
conda activate seismology
sacpz="/mnt/scratch/xiziyi/process_seed/fnet/sacpz"
seed="/mnt/research/seismolab2/japan_slab/data/processed_seed/fnet"
data="/mnt/research/seismolab2/japan_slab/data/fnet/data"
PY="/mnt/home/xiziyi/anaconda3/envs/seismology/bin/python"

# cd
cd /mnt/home/xiziyi/SeisScripts/slurm                ### change to the directory where your code is located

# python process_seed.py
srun -n 50 $PY ../process_seed/seed/process_seed.py --main_path $data

# python after_structure.py
$PY ../../data/process/handle_cea_directory_structure/after_structure.py --processedurl $data --seedurl $seed --sacpzurl $sacpz

scontrol show job $SLURM_JOB_ID     ### write job information to output file