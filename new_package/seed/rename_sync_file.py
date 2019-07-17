"""
rename generated sync asdf file based on the cmt solution files. (relocation)
"""
import subprocess
import click
import obspy
from os.path import join
from glob import glob


def rename_single(mapper, filepath):
    # filename = filepath.split("/")[-1]
    # filename_new = mapper[filename]
    # filepath_new = join(".".join(filename[:-1]), filename_new)
    filename = filepath.split("/")[-1]
    key = filename.split(".")[0].split("_")[1]
    key_new = mapper(key)
    all_split = filename.split(".")[0].split("_")
    all_split[1] = key_new
    filename_new = "_".join(all_split)+".h5"
    filepath_new = join("/".join(filepath.split("/")[:-1]), filename_new)

    subprocess.call(f"mv {filepath} {filepath_new}", shell=True)


def get_mapper(cmts_dir):
    event_path = glob(join(cmts_dir, "*"))
    event_name = [item.split("/")[-1] for item in event_path]
    result = {}
    for path, name in zip(event_path, event_name):
        event = obspy.read_events(event_path)[0]
        id = event.origins[0].resource_id.id.split("/")[-2]
        result[name] = id


def main(cmts_dir, files_dir):
    all_files = glob(join(files_dir, "*"))
