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


def cal_misfit(windows, obs_trace, syn_trace, freqmin, freqmax):
    result = {
        "pn": None,
        "p": None,
        "s": None,
        "surf_rs": None,
        "surf": None
    }

    for key in windows:
        if(windows[key] != None):
            if(key != "surf"):
                result[key] = cal_rs(
                    windows[key][0], windows[key][1], obs_trace, syn_trace)
            else:
                result[key] = cal_spec(
                    windows[key][0], windows[key][1], obs_trace, syn_trace, freqmin, freqmax)

    if(result["surf"] != None):
        key = "surf"
        result["surf_rs"] = cal_rs(
            windows[key][0], windows[key][1], obs_trace, syn_trace)

    return result


def cal_waveform_similarity(starttime, endtime, obs, syn):
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


def cal_rs(starttime, endtime, obs_trace, syn_trace):
    obs = obs_trace.slice(starttime, endtime).data
    syn = syn_trace.slice(starttime, endtime).data

    # perform CAP
    cor = np.correlate(syn, obs, mode='full')
    cs = int(np.where(cor == np.max(cor))[0][0])-int(len(obs))
    #print("time shift: "+str(0.1*cs))
    if(cs > 0):
        obs_trim = obs[0:len(obs)-cs]
        syn_trim = syn[cs:]
    else:
        cs = np.abs(cs)
        obs_trim = obs[cs:]
        syn_trim = syn[0:len(syn)-cs]
    misfit = np.sqrt(np.sum((obs_trim-syn_trim)**2))
    return misfit


def cal_spec(starttime, endtime, obs_trace, syn_trace, freqmin, freqmax):
    obs = obs_trace.slice(starttime, endtime).data
    syn = syn_trace.slice(starttime, endtime).data

    # dt is the delta for obs_trace
    dt = obs_trace.stats.delta

    # perform rayleigh wave multitaper spectrum measurement
    specobs, freq = mft.multitaper.mtspec(
        obs, dt, time_bandwidth=3.5)  # returns power spectrum
    specsyn, freq = mft.multitaper.mtspec(syn, dt, time_bandwidth=3.5)
    freqs = np.where(freq >= freqmin)[0][0]
    freqe = np.where(freq > freqmax)[0][0] - 1
    specobs = specobs[freqs:freqe]
    specsyn = specsyn[freqs:freqe]
    misfit = np.sum(np.abs(np.log10(specobs / specsyn)) /
                    len(specobs))   # absolute value
    return misfit


def get_amp_timelen_values(windows, st, st_syn):
    result = {
        "r": {},
        "t": {},
        "z": {}
    }
    result_time = {
        "r": {},
        "t": {},
        "z": {}
    }
    # r
    trace = st[0]
    trace_syn = st_syn[0]
    for key in windows:
        if(windows[key] == None):
            result["r"][key] = None
            result_time["r"][key] = None
        else:
            starttime = windows[key][0]
            endtime = windows[key][1]
            data = trace.slice(starttime, endtime).data
            result["r"][key] = np.max(np.abs(data))
            result_time["r"][key] = endtime-starttime
            data_syn = trace_syn.slice(starttime, endtime).data
            ratio = np.max(np.abs(data))/np.max(np.abs(data_syn))
            if(ratio > 3 or ratio < 1/3):
                result["r"][key] = None
    # t
    trace = st[1]
    trace_syn = st_syn[1]
    for key in windows:
        if(windows[key] == None):
            result["t"][key] = None
            result_time["t"][key] = None
        else:
            starttime = windows[key][0]
            endtime = windows[key][1]
            data = trace.slice(starttime, endtime).data
            result["t"][key] = np.max(np.abs(data))
            result_time["t"][key] = endtime-starttime
            data_syn = trace_syn.slice(starttime, endtime).data
            ratio = np.max(np.abs(data))/np.max(np.abs(data_syn))
            if(ratio > 3 or ratio < 1/3):
                result["t"][key] = None
    # z
    trace = st[2]
    trace_syn = st_syn[2]
    for key in windows:
        if(windows[key] == None):
            result["z"][key] = None
            result_time["z"][key] = None
        else:
            starttime = windows[key][0]
            endtime = windows[key][1]
            data = trace.slice(starttime, endtime).data
            result["z"][key] = np.max(np.abs(data))
            result_time["z"][key] = endtime-starttime
            data_syn = trace_syn.slice(starttime, endtime).data
            ratio = np.max(np.abs(data))/np.max(np.abs(data_syn))
            if(ratio > 3 or ratio < 1/3):
                result["z"][key] = None
    return result, result_time


@click.command()
@click.option('--obs_path', required=True, type=str, help="the obs hdf5 file path")
@click.option('--syn_path', required=True, type=str, help="the syn hdf5 file path")
@click.option('--max_period', required=True, type=float, help="the max period used")
@click.option('--min_period', required=True, type=float, help="the min period used")
@click.option('--status', required=True, type=str, help="either body or surf, since surface waves will use a different frequency band")
@click.option('--logfile', required=True, type=str, help="the log file path")
@click.option('--jsonfile', required=True, type=str, help="the outputed json file path")
def main(obs_path, syn_path, max_period, min_period, status, logfile, jsonfile):
    freqmin = 1.0/max_period
    freqmax = 1.0/min_period
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
        result = {
            "misfit_r": None,  # the misfit dict
            "misfit_t": None,  # the misfit dict
            "misfit_z": None,  # the misfit dict
            "property_times": None,
        }

        waveform_tags = sg_obs.get_waveform_tags()
        inv_obs = sg_obs["StationXML"]
        station_info = {inv_obs.get_contents()['stations'][0]}
        if(len(waveform_tags) == 0):
            logger.info(f"[{rank}/{size}] {station_info}: no data")
            return None  # no data for this station

        tag_obs = waveform_tags[0]
        tag_syn = sg_syn.get_waveform_tags()[0]
        st_obs_raw = sg_obs[tag_obs]
        st_syn_raw = sg_syn[tag_syn]

        # since we couldn't return a float32, we have to modify st to float64
        st_obs = st_obs_raw.copy()
        st_syn = st_syn_raw.copy()
        for trace in st_obs:
            trace.data = np.require(trace.data, dtype="float64")
        for trace in st_syn:
            trace.data = np.require(trace.data, dtype="float64")

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

        # get misfit
        result["misfit_r"] = cal_misfit(
            windows, st_obs[0], st_syn[0], freqmin, freqmax)
        result["misfit_t"] = cal_misfit(
            windows, st_obs[1], st_syn[1], freqmin, freqmax)
        result["misfit_z"] = cal_misfit(
            windows, st_obs[2], st_syn[2], freqmin, freqmax)

        # other parameters
        result["property_times"] = property_times

        # output log information
        windows_numbers = 0
        for key in windows:
            if(windows[key] != None):
                windows_numbers += 1
        logger.info(
            f"[{rank}/{size}] {station_info}: win_num:{windows_numbers} misfit_r:{result['misfit_r']} misfit_t:{result['misfit_t']} misfit_z:{result['misfit_z']}")

        # we should collect information of the max amplitude for normalization
        amp_values, time_length_values = get_amp_timelen_values(
            windows, st_obs, st_syn)

        # result -> json
        result_json = {
            "misfit_r": {
                "pn": result["misfit_r"]["pn"],
                "p": result["misfit_r"]["p"],
                "s": result["misfit_r"]["s"],
                "surf_rs": result["misfit_r"]["surf_rs"],
                "surf": result["misfit_r"]["surf"]
            },
            "misfit_t": {
                "pn": result["misfit_t"]["pn"],
                "p": result["misfit_t"]["p"],
                "s": result["misfit_t"]["s"],
                "surf_rs": result["misfit_t"]["surf_rs"],
                "surf": result["misfit_t"]["surf"]
            },
            "misfit_z": {
                "pn": result["misfit_z"]["pn"],
                "p": result["misfit_z"]["p"],
                "s": result["misfit_z"]["s"],
                "surf_rs": result["misfit_z"]["surf_rs"],
                "surf": result["misfit_z"]["surf"]
            },
            "property_times": {
                "first_p": property_times["first_p"],
                "first_s": property_times["first_s"],
                "surface_wave": property_times["surface_wave"],
                "local_station": property_times["local_station"],  # bool
                "gcarc": property_times["gcarc"],
                "azimuth": property_times["azimuth"]
            },
            "amplitude": {
                "r": {
                    "pn": amp_values["r"]["pn"],
                    "p": amp_values["r"]["p"],
                    "s": amp_values["r"]["s"],
                    "surf": amp_values["r"]["surf"]
                },
                "t": {
                    "pn": amp_values["t"]["pn"],
                    "p": amp_values["t"]["p"],
                    "s": amp_values["t"]["s"],
                    "surf": amp_values["t"]["surf"]
                },
                "z": {
                    "pn": amp_values["z"]["pn"],
                    "p": amp_values["z"]["p"],
                    "s": amp_values["z"]["s"],
                    "surf": amp_values["z"]["surf"]
                }
            },
            "window_length": {
                "r": {
                    "pn": time_length_values["r"]["pn"],
                    "p": time_length_values["r"]["p"],
                    "s": time_length_values["r"]["s"],
                    "surf": time_length_values["r"]["surf"]
                },
                "t": {
                    "pn": time_length_values["t"]["pn"],
                    "p": time_length_values["t"]["p"],
                    "s": time_length_values["t"]["s"],
                    "surf": time_length_values["t"]["surf"]
                },
                "z": {
                    "pn": time_length_values["z"]["pn"],
                    "p": time_length_values["z"]["p"],
                    "s": time_length_values["z"]["s"],
                    "surf": time_length_values["z"]["surf"]
                }
            }
        }

        return result_json

    # here we have a dict, the key is {network}.{station}, and the value is the returned result.
    if(isroot):
        gcmt_id = origin.resource_id.id.split("/")[-2]
        logger.info(
            f"start to calculate misfit for {gcmt_id}, with {status}, from {min_period} to {max_period}")
    results = obs_ds.process_two_files_without_parallel_output(syn_ds, process)

    with open(jsonfile, 'w') as fp:
        json.dump(results, fp)

    if(isroot):
        logger.success(f"success for event {gcmt_id}")


if __name__ == "__main__":
    main()
