"""
mainly for fdsn stations, as F-net and cea almost contribute all events.
"""
from glob import glob
from os.path import join
import numpy as np


def count_stations(base_path, station_ids):
    event_dirs = glob(join(base_path, "*"))
    contribution = np.zeros(len(station_ids), dtype=np.int)
    for index_station, id in enumerate(station_ids):
        print(index_station, id)
        for dir in event_dirs:
            allfiles = glob(join(dir, "*"))
            status = False
            for item in allfiles:
                if(id in item):
                    status = True
            if(status):
                contribution[index_station] += 1
    return contribution


def get_station_ids(base_path):
    stationlist_path = "../data/fdsn.stations"
    fdsn_list = np.loadtxt(stationlist_path, dtype=np.str)
    fnet_list = np.loadtxt("../data/fnet.stations", dtype=np.str)
    cea_list = np.loadtxt("../data/cea.stations", dtype=np.str)

    station_ids = []
    for row in fdsn_list:
        station_name = row[0]
        network_name = row[1]
        station_ids.append(f"{network_name}.{station_name}")
    contribution = count_stations(base_path, station_ids)
    with open("../data/station_count.log", "w") as f:
        for row, cont_item in zip(fdsn_list, contribution):
            f.write(f"{row[3]} {row[2]} {cont_item} \n")
        for row in fnet_list:
            f.write(f"{row[3]} {row[2]} 284 \n")
        for row in cea_list:
            f.write(f"{row[3]} {row[2]} 284 \n")


def main():
    base_path = "/mnt/research/seismolab2/japan_slab/data/fdsn/data"
    get_station_ids(base_path)


if __name__ == "__main__":
    main()
