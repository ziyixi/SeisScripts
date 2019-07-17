"""
This is the serial version.
"""
import click
from mpi4py import MPI
from glob import glob
from os.path import join
import numpy as np
from generate_sync_asdf_specfem import convert_sync_to_asdf

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
isroot = (rank == 0)


def get_directories_to_handle(all_dirs):
    return np.array_split(all_dirs, size)[rank]


@click.command()
@click.option('--base_dir', required=True, type=str, help="the relocation working directory")
@click.option('--out_dir', required=True, type=str, help="the asdf output directory")
def main(base_dir, out_dir):
    all_dirs = glob(join(base_dir, "*", "*"))
    dirs_to_handle = get_directories_to_handle(all_dirs)
    for each_dir in dirs_to_handle:
        print(f"[{rank}] start to handle {each_dir}")
        split_path = each_dir.split("/")
        event = split_path[-2]
        depth = split_path[-1]
        output_path = join(out_dir, f"sync_{event}_{depth}_raw.h5")
        convert_sync_to_asdf(each_dir, output_path, True)


if __name__ == "__main__":
    main()
