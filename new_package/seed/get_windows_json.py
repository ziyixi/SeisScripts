"""
calculate misfit between sync and data.
"""
import json

import click
import mtspec as mft
import numpy as np
import obspy
import pyasdf
from loguru import logger
from mpi4py import MPI
from obspy.geodetics.base import gps2dist_azimuth, locations2degrees
from obspy.taup import TauPyModel

model = TauPyModel(model='ak135')
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
isroot = (rank == 0)


def get_property_times(stla, stlo, evla, evlo, evdp):
    property_times = {
        "first_p": None,
        "first_s": None,
        "surface_wave": None,
        "local_station": False,
        "gcarc": None,
        "azimuth": None
    }

    # sphere gcircle distance, since taup use sphere
    gcarc = locations2degrees(stla, stlo, evla, evlo)
    property_times["gcarc"] = gcarc

    # calculate first arrivals
    arrivals = model.get_travel_times(source_depth_in_km=evdp,
                                      distance_in_degree=gcarc,
                                      phase_list=["p", "P", "s", "S", "3.5kmps"])

    for item in arrivals:
        # find p
        if(property_times["first_p"] == None):
            if(item.name == "p" or item.name == "P"):
                property_times["first_p"] = item.time

        # find s
        if(property_times["first_s"] == None):
            if(item.name == "s" or item.name == "S"):
                property_times["first_s"] = item.time

        # find surface wave
        if(property_times["surface_wave"] == None):
            if(item.name == "3.5kmps"):
                property_times["surface_wave"] = item.time

    # see if it's local stations:
    for item in arrivals:
        if(item.name == "p" or item.name == "s"):
            property_times["local_station"] = True
            break
        elif(item.name == "P" or item.name == "S"):
            property_times["local_station"] = False
            break

    # get azimuth, from the source to the stations
    _, property_times["azimuth"], _ = gps2dist_azimuth(evla, evlo, stla, stlo)

    # always could success
    return property_times


def get_windows(starttime, endtime,  property_times):
    ptime = property_times["first_p"]
    stime = property_times["first_s"]
    surftime = property_times["surface_wave"]
    is_close = property_times["local_station"]
    gcarc = property_times["gcarc"]

    result = {
        "pn": None,
        "p": None,
        "s": None,
        "surf": None
    }

    # different conditions
    if(gcarc < 10):  # local stations
        if(is_close):
            result["pn"] = (starttime, starttime+60)
        else:
            if(ptime < 20):
                result["pn"] = (starttime, starttime+stime)
                result["surf"] = (starttime+stime, starttime+stime+60)
            elif(20 <= ptime < 60):
                result["pn"] = (starttime+ptime-10, starttime+ptime+30)
                result["surf"] = (starttime+stime-10, starttime+stime+110)
            else:
                result["pn"] = (starttime+ptime-20, starttime+ptime+60)
                result["surf"] = (starttime+stime-10, starttime+stime+180)
    else:  # regional stations
        win_surface_start = starttime+surftime - 40
        win_surface_end = starttime+surftime + 180

        result["p"] = (starttime+ptime-20, starttime+ptime+60)
        result["s"] = (starttime+stime-20, starttime+stime+80)
        if(endtime-win_surface_start < 100):
            pass
        elif(win_surface_end > endtime):
            result["surf"] = (win_surface_start, endtime)
        else:
            result["surf"] = (win_surface_start, win_surface_end)

    return result


def cal_waveform_similarity(starttime, endtime, obs, syn):
    # asdf stream is in the order of r,t,z
    obs_r = obs[0].slice(starttime, endtime).data
    obs_t = obs[1].slice(starttime, endtime).data
    obs_z = obs[2].slice(starttime, endtime).data

    syn_r = syn[0].slice(starttime, endtime).data
    syn_t = syn[1].slice(starttime, endtime).data
    syn_z = syn[2].slice(starttime, endtime).data

    similarity = np.sum(np.abs(obs_r*syn_r) +
                        np.abs(obs_t*syn_t)+np.abs(obs_z*syn_z))/np.sqrt(np.sum(obs_r*obs_r+obs_t*obs_t+obs_z*obs_z)*np.sum(syn_r*syn_r+syn_t*syn_t+syn_z*syn_z))
    return similarity


def filter_windows(windows, obs, syn, status):
    # since the frequency band for the body wave and the surface wave is different, we should consider status
    if(status == "body"):
        for key in windows:
            if(key == "surf"):
                windows[key] = None
    elif(status == "surf"):
        for key in windows:
            if(key != "surf"):
                windows[key] = None
    else:
        for key in windows:
            windows[key] = None

    # compare similarity
    for key in windows:
        if(windows[key] != None):
            CCT = cal_waveform_similarity(
                windows[key][0], windows[key][1], obs, syn)
            if(CCT < 0.5):
                windows[key] = None
    return windows

@click.command()
@click.option('--obs_path', required=True, type=str, help="the obs hdf5 file path")
@click.option('--syn_path', required=True, type=str, help="the syn hdf5 file path")
@click.option('--status', required=True, type=str, help="either body or surf, since surface waves will use a different frequency band")
@click.option('--logfile', required=True, type=str, help="the log file path")
@click.option('--jsonfile', required=True, type=str, help="the outputed json file path")
def main(obs_path, syn_path, status, logfile, jsonfile):
    obs_ds = pyasdf.ASDFDataSet(obs_path)
    syn_ds = pyasdf.ASDFDataSet(syn_path)
    event = obs_ds.events[0]
    origin = event.preferred_origin() or event.origins[0]
    evla = origin.latitude
    evlo = origin.longitude
    evdp = origin.depth/1000

    # add logger information
    logger.add(logfile, format="{time} {level} {message}", level="INFO")

    # kernel function
    def process(sg_obs, sg_syn):

        waveform_tags = sg_obs.get_waveform_tags()
        inv_obs = sg_obs["StationXML"]
        station_info = {inv_obs.get_contents()['stations'][0]}

        tag = waveform_tags[0]  # should have only one tag, after we have simplify the asdf file
        st_obs = sg_obs[tag]
        st_syn = sg_syn["sync"]

        # property times
        stla = inv_obs[0][0].latitude
        stlo = inv_obs[0][0].longitude
        property_times = get_property_times(stla, stlo, evla, evlo, evdp)

        # get windows
        starttime = st_obs[0].stats.starttime
        endtime = st_obs[0].stats.endtime
        windows = get_windows(starttime, endtime,  property_times)

        # discard windows
        windows = filter_windows(windows, st_obs, st_syn, status)

        # output log information
        windows_numbers = 0
        for key in windows:
            if(windows[key] != None):
                windows_numbers += 1
        logger.info(
            f"[{rank}/{size}] {station_info}: win_num:{windows_numbers}")

        return windows

    # here we have a dict, the key is {network}.{station}, and the value is the returned result.
    if(isroot):
        gcmt_id = origin.resource_id.id.split("/")[-2]
        logger.info(
            f"start to get windows for {gcmt_id}, with {status}")
    results = obs_ds.process_two_files_without_parallel_output(syn_ds, process)

    with open(jsonfile, 'w') as fp:
        json.dump(results, fp)

    if(isroot):
        logger.success(f"success for event {gcmt_id}, store in {jsonfile}")


if __name__ == "__main__":
    main()
