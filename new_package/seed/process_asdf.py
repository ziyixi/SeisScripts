"""
the other script has problem in using pyasdf, use serial IO instead.
"""
from mpi4py import MPI
import pyasdf
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def set_scatter_list(ds, tag):
    """
    only for the root process
    """
    name_list = ds.waveforms.list()
    name_list_collection = np.array_split(name_list, size)

    # get waveform data for each rank
    waveform_list = [ds.waveforms[name_item][tag]
                     for name_item in name_list]
    waveform_list_collection = np.array_split(waveform_list, size)

    # get station_xml data for each rank
    stationxml_list = [ds.waveforms[name_item]["StationXML"]
                       for name_item in name_list]
    stationxml_list_collection = np.array_split(stationxml_list, size)

    # get event_xml information
    event = ds.events[0]

    return name_list_collection, waveform_list_collection, stationxml_list_collection, event


def distribute_data(name_list_collection, waveform_list_collection, stationxml_list_collection, event):
    name_list_this_rank = None
    waveform_list_this_rank = None
    stationxml_list_this_rank = None
    event_this_rank = None

    name_list_this_rank = comm.scatter(name_list_collection, root=0)
    waveform_list_this_rank = comm.scatter(waveform_list_collection, root=0)
    stationxml_list_this_rank = comm.scatter(
        stationxml_list_collection, root=0)
    event_this_rank = comm.bcast(event, event=0)

    return name_list_this_rank, waveform_list_this_rank, stationxml_list_this_rank, event_this_rank


def process_data(st, inv, event, name):
    try:
        length = len(st)
        print(f"#{rank} {name} {length}")
        return st
    except:
        print(f"#{rank} {name} problems!")
        return None


def process_in_each_rank(name_list_this_rank, waveform_list_this_rank, stationxml_list_this_rank, event_this_rank):
    result_sts = []
    for st, inv, name in zip(waveform_list_this_rank, stationxml_list_this_rank, name_list_this_rank):
        result_st = process_data(st, inv, event_this_rank, name)
        result_sts.append(result_st)
    return result_sts


def main(asdf_fname, tag):
    isroot = (rank == 0)

    name_list_collection, waveform_list_collection, stationxml_list_collection, event = None, None, None, None
    if(isroot):
        ds = pyasdf.ASDFDataSet(asdf_fname)
        name_list_collection, waveform_list_collection, stationxml_list_collection, event = set_scatter_list(
            ds, tag)

    # distribute data
    name_list_this_rank, waveform_list_this_rank, stationxml_list_this_rank, event_this_rank = distribute_data(
        name_list_collection, waveform_list_collection, stationxml_list_collection, event)

    comm.barrier()

    # process data in each process
    process_in_each_rank(name_list_this_rank, waveform_list_this_rank,
                         stationxml_list_this_rank, event_this_rank)

    # finish
    if(isroot):
        del ds


if __name__ == "__main__":
    asdf_fname = "/mnt/home/xiziyi/SeisScripts/new_package/seed/example.h5"
    tag = "raw"
    main(asdf_fname, tag)
