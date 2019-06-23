"""
add head information to fnet data
"""
import obspy
import click
import os
import sys
import datetime
import subprocess
from os.path import join


def read_eventml(xml_path):
    events = obspy.read_events(xml_path)
    result = {}
    for item in events:
        key = item.origins[0].resource_id.id.split("/")[2]
        result[key] = {
            "time": item.origins[0].time.datetime,
            "evlo": item.origins[0].longitude,
            "evla": item.origins[0].latitude,
            "evdp": item.origins[0].depth / 1000,
            "mag": item.magnitudes[0].mag
        }
    return result


@click.command()
@click.option('--xml_path', required=True, help="the xml file", type=str)
@click.option('--main_path', required=True, help="the data directory", type=str)
def main(xml_path, main_path):
    os.putenv("SAC_DISPLAY_COPYRIGHT", '0')
    event_info = read_eventml(xml_path)
    for key in event_info:
        data = event_info[key]
        o = data["time"]
        jday = o.strftime("%j")
        msec = int(o.microsecond / 1000 + 0.5)

        dirname = join(main_path, key)
        os.chdir(dirname)

        s = "wild echo off \n"
        s += "r *.SAC \n"
        s += "synchronize \n"
        s += "ch o gmt {} {} {} {} {} {}\n".format(o.year, jday, o.hour,
                                                   o.minute, o.second, msec)
        s += "ch allt (0 - &1,o&) iztype IO \n"
        s += "ch evlo {} evla {} evdp {} mag {} \n".format(
            data["evlo"], data["evla"], data["evdp"], data["mag"])
        s += "wh \n"
        s += "q \n"
        subprocess.Popen(
            ['sac'], stdin=subprocess.PIPE).communicate(s.encode())

        os.chdir(main_path)


if __name__ == "__main__":
    main()
