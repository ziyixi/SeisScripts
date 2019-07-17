#!/bin/bash --login
########## SBATCH Lines for Resource Request ##########
 
#SBATCH --time=05:00:00             # limit of wall clock time - how long the job will run (same as -t)
#SBATCH --ntasks=300                  # number of tasks - how many tasks (nodes) that you require (same as -n)
#SBATCH --mem-per-cpu=4G            # memory required per allocated CPU (or core) - amount of memory (in bytes)
#SBATCH --job-name process_sync_asdf      # you can give your job a name for easier identification (same as -J)
 
########## Command Lines to Run ##########
RAW_DIR=/mnt/ls15/scratch/users/xiziyi/process_asdf/relocation/raw_sync
PROCESSED_DIR=/mnt/ls15/scratch/users/xiziyi/process_asdf/relocation/processed
min_periods=10,20,40
max_periods=120,120,120
waveform_length=2400
sampling_rate=10
logfile=/mnt/ls15/scratch/users/xiziyi/process_asdf/relocation/processed_for_first_iteration_validation.log
cmts_dir=/mnt/research/seismolab2/japan_slab/cmts/cmts_from_new_cea_disk

module purge
module load GCC/8.2.0-2.31.1
module load OpenMPI/3.1.3  ### load necessary modules, e.g.

PY=/mnt/home/xiziyi/anaconda3/envs/seismology/bin/python
. activate seismology
 
cd /mnt/home/xiziyi/script/SeisScripts/new_package/seed                  ### change to the directory where your code is located

# rename file names
# $PY rename_sync_file.py --cmts_dir $cmts_dir --files_dir $RAW_DIR

for filename in $RAW_DIR/*.h5; do 
    # rename FNET->BO
    $PY rename_fnet.py --asdf_file $filename
    # process
    echo $filename
    srun -n 300 $PY process_sync.py --min_periods $min_periods --max_periods $max_periods --asdf_filename $filename --waveform_length $waveform_length --sampling_rate $sampling_rate --output_directory $PROCESSED_DIR --logfile $logfile
done

scontrol show job $SLURM_JOB_ID     ### write job information to output file