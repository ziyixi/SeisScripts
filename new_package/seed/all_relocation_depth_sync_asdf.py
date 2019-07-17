"""
This is the serial version.
"""
import click
# from mpi4py import MPI
from glob import glob
from os.path import join
import numpy as np
from generate_sync_asdf_specfem import convert_sync_to_asdf
import multiprocessing
from functools import partial
# ! no print, we have to find a way to log the process


# comm = MPI.COMM_WORLD
# rank = comm.Get_rank()
# size = comm.Get_size()
# isroot = (rank == 0)

def kernel(each_dir, out_dir):
    print(f"start to handle {each_dir}")
    split_path = each_dir.split("/")
    event = split_path[-2]
    depth = split_path[-1]
    output_path = join(out_dir, f"sync_{event}_{depth}_raw.h5")
    files_in_output = glob(join(out_dir, "*"))
    if(output_path in files_in_output):
        return
    convert_sync_to_asdf(each_dir, output_path, True)
    print(f"finish handling {each_dir}")


@click.command()
@click.option('--base_dir', required=True, type=str, help="the relocation working directory")
@click.option('--out_dir', required=True, type=str, help="the asdf output directory")
def main(base_dir, out_dir):
    all_dirs = glob(join(base_dir, "*", "*"))
#     for each_dir in all_dirs:
#         print(f"start to handle {each_dir}")
#         split_path = each_dir.split("/")
#         event = split_path[-2]
#         depth = split_path[-1]
#         output_path = join(out_dir, f"sync_{event}_{depth}_raw.h5")
#         files_in_output = glob(join(out_dir, "*"))
#         if(output_path in files_in_output):
#             continue

#         convert_sync_to_asdf(each_dir, output_path, True)
#         print(f"finish handling {each_dir}")

    with multiprocessing.Pool(processes=9) as pool:
        pool.map(partial(kernel, out_dir=out_dir), all_dirs)


if __name__ == "__main__":
    main()
