"""
generate event list in the form of "2018/04/17 02:39:15.0    1.29  126.88  82 4.9 Mw"
"""
from glob import glob
import obspy
from os.path import join

cmts_path = "/Users/ziyixi/work/Datas/cmts/cmts"


def get_line_for_event(event):
    origin = event.preferred_origin() or event.origins[0]
    evla = origin.latitude
    evlo = origin.longitude
    evdp = origin.depth/1000
    mag = event.magnitudes[0].mag
    magnitude_type = event.magnitudes[0].magnitude_type
    utctime = origin.time
    if(utctime.year < 1000):
        utctime.year += 2000
    utc_start = utctime-120
    utc_end = utctime+60*45
    thetime = utctime.datetime.strftime("%Y/%m/%d %H:%M:%S.%f")
    thestart = utc_start.datetime.strftime("%Y/%m/%d %H:%M:%S.%f")
    theend = utc_end.datetime.strftime("%Y/%m/%d %H:%M:%S.%f")
    gcmtid = origin.resource_id.id.split("/")[-2]
    if(gcmtid[:2] == "00"):
        gcmtid = "20"+gcmtid[2:]
    return f"{gcmtid} {thestart}   {theend} {evla:>9.4f} {evlo:>9.4f} {evdp:>4.0f} {mag:.2f} {magnitude_type}\n"


def get_time(event):
    origin = event.preferred_origin() or event.origins[0]
    utctime = origin.time
    if(utctime.year < 1000):
        utctime.year += 2000
    return utctime


def main():
    events = obspy.read_events(join(cmts_path, "*"))
    sorted_events = sorted(events, key=lambda event: get_time(event))
    with open("time_window.txt", "w") as f:
        for item in sorted_events:
            f.write(get_line_for_event(item))


if __name__ == "__main__":
    main()
