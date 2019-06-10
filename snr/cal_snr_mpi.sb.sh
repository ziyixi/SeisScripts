#!/bin/bash --login
########## SBATCH Lines for Resource Request ##########

#SBATCH --time=04:00:00             # limit of wall clock time - how long the job will run (same as -t)
#SBATCH --ntasks=95           # number of tasks - how many tasks (nodes) that you require (same as -n)
#SBATCH --job-name snr_mpi      # you can give your job a name for easier identification (same as -J)
#SBATCH --mem-per-cpu=8G

########## Command Lines to Run ##########

. activate seismology
PY=""

srun -n 95 PY cal_snr_mpi.py        ### call your executable (similar to mpirun)

scontrol show job $SLURM_JOB_ID     ### write job information to output file