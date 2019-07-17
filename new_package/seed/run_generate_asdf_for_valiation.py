import subprocess
from glob import glob
from os.path import join

output_dir = "/mnt/research/seismolab2/japan_slab/data/asdf_for_validation"
cmtids_raw = glob(
    "/mnt/research/seismolab2/japan_slab/cmts/Japan_slab_validation/*")
cmtids_raw = [item.split("/")[-1] for item in cmtids_raw]

# remove inished asdf file
finished = glob(join(output_dir, "*"))
finished = [item.split("/")[-1] for item in finished]
finished = [item.split(".")[0] for item in finished]
finished = [item.split("_")[-1] for item in finished]
cmtids = []
for item in cmtids_raw:
    if(not (item in finished)):
        cmtids.append(item)
print(cmtids)

seed_dir = "/mnt/research/seismolab2/japan_slab/data/data_for_validation"
cmt_dir = "/mnt/research/seismolab2/japan_slab/cmts/Japan_slab_validation"

for cmtid in cmtids:
    seed_directory = join(seed_dir, cmtid)
    cmt_path = join(cmt_dir, cmtid)
    output_path = join(output_dir, f"raw_{cmtid}.h5")
    logfile = "./log_validation"
    command = f"python generate_asdf_normal.py --seed_directory {seed_directory} --cmt_path {cmt_path} --output_path {output_path} --logfile {logfile} --with_mpi"
    subprocess.call(command, shell=True)
