"""
A script to automatically download the f-net data.
"""
from datetime import datetime
from os.path import isfile, join, isdir

import click
import numpy as np
import obspy
import sh
from FnetPy import Client
from logbook import FileHandler, Logger
from tqdm import tqdm


def get_download_dict(events):
    result = {}
    for event in events:
        starttime = event.origins[0].time - 2 * 60
        starttime = starttime.datetime
        name = event.resource_id.id.split("/")[2]
        result[name] = starttime
    return result


def download_seed_kernel(client, main_directory, name, starttime):
    save_path = join("./.data", f"{name}.SEED")
    status = client.get_waveform(
        starttime, duration_in_seconds=42 * 60, filename=save_path)
    return status


@click.command()
@click.option("--event_info", required=True, help="event info pickle file", type=str)
@click.option("--main_directory", required=True, help="the working directory", type=str)
@click.option("--username", required=True, help="the username for Fnet", type=str)
@click.option("--password", required=True, help="the password for Fnet", type=str)
def main(event_info, main_directory, username, password):
    # set up logging
    log_handler = FileHandler(join(main_directory, "log"))
    log_handler.push_application()
    log = Logger("fnet_log")

    # fix path bug in FnetPy
    sh.mkdir("-p", join(main_directory, "data"))
    try:
        sh.unlink("./.data")
    except:
        pass
    sh.ln("-s", join(main_directory, "data"), "./.data")

    client = Client(username, password)
    events = obspy.read_events(event_info)
    download_dict = get_download_dict(events)
    all_events_set = set(download_dict)

    # save to all.filelist
    with open(join(main_directory, "all.filelist"), "w") as f:
        for item in sorted(list(all_events_set)):
            f.write(f"{item}\n")

    if isfile(join(main_directory, "local.filelist")):
        downloaded_file_array = np.loadtxt(
            join(main_directory, "local.filelist"), dtype=np.str)
        # if only downloaded 1 event, redownload all
        try:
            downloaded_set = set(
                downloaded_file_array
            )
        except:
            downloaded_set = set()
    else:
        downloaded_set = set()
    todownload = all_events_set - downloaded_set

    # start to download
    for key in tqdm(todownload):
        log.info(f"start to download {key}")
        status = download_seed_kernel(
            client, main_directory, key, download_dict[key])
        with open(join(main_directory, "local.filelist"), "a") as f:
            if(status != None):
                f.write(f"{key}\n")
                log.info(f"finish downloading {key}")
            else:
                log.info(f"fail in downloading {key}")
    log.info("success")


if __name__ == "__main__":
    main()
