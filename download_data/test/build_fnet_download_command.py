"""
A script to build the command line text for downloading fnet data in the website.
    @problem contain more stations so that "no avaliable data for some selections"
"""
import obspy
import numpy as np
import sys
import pyperclip


def get_download_dict(events):
    result = {}
    for event in events[int(sys.argv[1]): int(sys.argv[1]) + 4]:
        starttime = event.origins[0].time - 2 * 60
        endtime = event.origins[0].time + 40 * 60
        starttime = starttime.datetime
        endtime = endtime.datetime
        name = event.resource_id.id.split("/")[2]
        result[name] = (
            starttime.strftime("%Y/%m/%d,%H:%M:%S"),
            endtime.strftime("%Y/%m/%d,%H:%M:%S"),
        )
    return result


def main():
    station_list = np.loadtxt("../data/fnet_stationlist", dtype=np.str)
    command = ""
    events = obspy.read_events("../data/event_info.xml")
    download_dict = get_download_dict(events)
    for key in download_dict:
        for item in station_list:
            command += (
                f"get {item} BHZ {download_dict[key][0]} {download_dict[key][1]}\n"
            )
            command += (
                f"get {item} BHN {download_dict[key][0]} {download_dict[key][1]}\n"
            )
            command += (
                f"get {item} BHE {download_dict[key][0]} {download_dict[key][1]}\n"
            )
    pyperclip.copy(command)


if __name__ == "__main__":
    main()
