#!/bin/bash --login
########## SBATCH Lines for Resource Request ##########
 
#SBATCH --time=01:00:00             # limit of wall clock time - how long the job will run (same as -t)
#SBATCH --ntasks=150                  # number of tasks - how many tasks (nodes) that you require (same as -n)
#SBATCH --mem-per-cpu=4G            # memory required per allocated CPU (or core) - amount of memory (in bytes)
#SBATCH --job-name process_sync_asdf      # you can give your job a name for easier identification (same as -J)
 
########## Command Lines to Run ##########
RAW_DIR=/mnt/research/seismolab2/japan_slab/data/asdf_for_validation
PROCESSED_DIR=/mnt/research/seismolab2/japan_slab/processed_data/processed_for_first_iteration_validation
SIMPLE_DIR=/mnt/research/seismolab2/japan_slab/relocation/for_first_iteration_validation/simplified
min_periods=10,20,40
max_periods=120,120,120
waveform_length=2400
sampling_rate=10
logfile=/mnt/research/seismolab2/japan_slab/processed_data/processed_for_first_iteration_validation.log

module purge
module load GCC/8.2.0-2.31.1
module load OpenMPI/3.1.3  ### load necessary modules, e.g.

PY=/mnt/home/xiziyi/anaconda3/envs/seismology/bin/python
. activate seismology
 
cd /mnt/home/xiziyi/script/SeisScripts/new_package/seed                  ### change to the directory where your code is located

for filename in $RAW_DIR/*.h5; do 
    # run process
    srun -n 150 $PY process_asdf_cea.py --min_periods $min_periods --max_periods $max_periods --asdf_filename $filename  --waveform_length $waveform_length --sampling_rate $sampling_rate  --output_directory $PROCESSED_DIR --logfile $logfile --correct_cea --cea_correction_file cmpaz_segment.txt
done

# remove empty stations
for filename in $PROCESSED_DIR/*.h5; do
    thebasename=`basename $filename`
    $PY simplify_asdf.py --asdf_file $filename --logfile $logfile --output_file $SIMPLE_DIR/$thebasename 
done

# 

scontrol show job $SLURM_JOB_ID     ### write job information to output file