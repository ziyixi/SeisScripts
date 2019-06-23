import sh
from glob import glob
from os.path import join
import pickle

cea_dir1 = "/mnt/research/seismolab2/japan_slab/data/upload_temp_ziyi/wangbs.20181105"
cea_dir2 = "/mnt/research/seismolab2/japan_slab/data/upload_temp_ziyi/20190325.SEED.garbage/seed"

# files in cea_dir1
search_path_1 = join(cea_dir1, "*", "*", "*")
allfiles1 = glob(search_path_1)

# files in cea_dir2
search_path_2 = join(cea_dir2, "*", "*")
allfiles2 = glob(search_path_2)

# all files
allfiles = allfiles1+allfiles2

# ref list
ref_dict = pickle.load(open("cmts_ref.pkl", "rb"))
target_dir = "/mnt/scratch/xiziyi/data/cea"

for cea_id in ref_dict:
    gcmt_id = ref_dict[cea_id]
    sh.mkdir("-p", join(target_dir, gcmt_id))

    # search all seed files
    for seed_file in allfiles:
        seed_name = seed_file.split("/")[-1]
        seed_id = seed_name.split(".")[0]
        if(cea_id == seed_id):
            sh.cp(seed_file, join(target_dir, gcmt_id))
    print(f"finish cp {gcmt_id}")
