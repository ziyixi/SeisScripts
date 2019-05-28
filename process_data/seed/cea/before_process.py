#!/usr/bin/envv python

import os
import sh
import glob
import click
import subprocess


@click.command()
@click.option('--old_path', required=True, help="the old path", type=str)
@click.option('--new_path', required=True, help="the new path", type=str)
def refine_structure(old_path, new_path):
    old_path, new_path = os.path.abspath(old_path), os.path.abspath(new_path)
    search_path = f"{old_path}/*/*/*SEED"
    seed_files = glob.glob(search_path)

    keys = set()
    for seed_file in seed_files:
        _, fname = os.path.split(seed_file)
        thekey = fname.split(".")[0]
        keys.add(thekey)

    for thekey in keys:
        fname = f"{new_path}/{thekey}"
        sh.mkdir("-p", fname)
        # sh.mv(f"{old_path}/*/*/{thekey}*SEED", fname)
        subprocess.call(f"mv {old_path}/*/*/{thekey}*SEED {fname}", shell=True)


if __name__ == "__main__":
    refine_structure()
