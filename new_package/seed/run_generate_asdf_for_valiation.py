import subprocess
from glob import glob
from os.path import join

cmtids = glob(
    "/mnt/research/seismolab2/japan_slab/cmts/Japan_slab_validation/*")
cmtids = [item.split("/")[-1] for item in cmtids]
seed_dir = "/mnt/research/seismolab2/japan_slab/data/data_for_validation"
output_dir = "/mnt/research/seismolab2/japan_slab/data/asdf_for_validation"
cmt_dir = "/mnt/research/seismolab2/japan_slab/cmts/Japan_slab_validation"

for cmtid in cmtids:
    seed_directory = join(seed_dir, cmtid)
    cmt_path = join(cmt_dir, cmtid)
    output_path = join(output_dir, f"raw_{cmtid}.h5")
    logfile = "./log_validation"
    command = f"python generate_asdf_normal.py --seed_directory {seed_directory} --cmt_path {cmt_path} --output_path {output_path} --logfile {logfile} --with_mpi"
    subprocess.call(command, shell=True)
