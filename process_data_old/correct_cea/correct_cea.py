import pandas as pd
from glob import glob
from os.path import join
import obspy
from loguru import logger
import sh
import click
from mpi4py import MPI
import os
import numpy as np

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
os.putenv("SAC_DISPLAY_COPYRIGHT", '0')
logger.add("correct_cea.log", format="{time} {level} {message}", level="INFO")


def read_reference(ref_path):
    ref = pd.read_csv(ref_path, sep="|")

    starttime = ref.starttime.values
    starttime = [obspy.UTCDateTime(item) for item in starttime]
    ref.starttime = starttime

    endtime = ref.endtime.values
    endtime = [obspy.UTCDateTime(item) for item in endtime]
    ref.endtime = endtime
    return ref


def get_events_list(cmts_path):
    urls = glob(join(cmts_path, "*"))
    result = [item.split("/")[-1] for item in urls]
    return result


def get_events_info(cmts_path, events_list):
    result = obspy.core.event.catalog.Catalog()
    for item in events_list:
        read_url = join(cmts_path, item)
        result += obspy.read_events(read_url)
    return result


def process_single_event(event_id, event_info, ref, work_path):
    allsac_path = glob(join(work_path, event_id, "*"))
    allsac = [item.split("/")[-1] for item in allsac_path]

    stdin_list = []
    stdin_list.append(f"wild echo off \n")
    for sacfile in allsac:
        infolist = sacfile.split(".")
        net = infolist[0]
        sta = infolist[1]
        chan = infolist[-1]

        event_time = event_info.origins[0].time

        if(event_time > obspy.UTCDateTime("2013-09-01")):
            logger.info(
                f"time newer than 2013-09-01 for {event_id}")
            break  # same events for the same directory

        event_ref = ref.loc[(ref.net == net) & (ref.sta == sta) & (
            event_time > ref.starttime) & (event_time < ref.endtime)]

        if(len(event_ref) == 0):
            logger.error(f"no reference for {sacfile} in {event_id}")
            continue

        if(len(event_ref) > 1):
            logger.warning(f"multiple references for {sacfile} in {event_id}")

        rotation_angle = -1*event_ref.median.values[0]

        readin_sacfiles = join(work_path, event_id, f"{net}.{sta}*[RT]")
        stdin_list.append(f"r {readin_sacfiles}\n")
        stdin_list.append(f"rotate through {rotation_angle} \n")
        stdin_list.append(f"write over \n")
        logger.info(f"processing  {sacfile} in {event_id}")

    stdin_list.append(f"q\n")
    sh.sac(_in=stdin_list)


def generate_paths(events_list, events_info):
    event_id_this_rank = np.array_split(events_list, size)[rank]
    event_info_this_rank = np.array_split(events_info, size)[rank]
    return event_id_this_rank, event_info_this_rank


@click.command()
@click.option('--cmts_path', required=True, help="the directory of cmt solutions", type=str)
@click.option('--work_path', required=True, help="the directory of data", type=str)
@click.option('--ref_path', required=True, help="the reference file", type=str)
def main(cmts_path, work_path, ref_path):
    ref = read_reference(ref_path)
    events_list = get_events_list(cmts_path)
    events_info = get_events_info(cmts_path, events_list)
    event_id_this_rank, event_info_this_rank = generate_paths(
        events_list, events_info)

    for event_id, event_info in zip(event_id_this_rank, event_info_this_rank):
        process_single_event(event_id, event_info, ref, work_path)
        logger.success(f"having processed {event_id}")

    logger.success("finished!")


if __name__ == "__main__":
    main()
