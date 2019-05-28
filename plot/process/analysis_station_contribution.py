"""
mainly for fdsn stations, as F-net and cea almost contribute all events.
"""
from glob import glob
from os.path import join


def count_stations(base_path, station_ids):
    event_dirs = glob(join(base_path, "*"))
