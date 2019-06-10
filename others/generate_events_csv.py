import pandas as pd
import obspy


def main():
    pandas_list = []
    events = obspy.read_events("./data/cmts/*")
    for id, value in enumerate(events):
        index = id+1
        eid = value.resource_id.id.split("/")[-2]

        time = value.origins[0].time
        year = time.year
        month = time.month
        day = time.day
        hr = time.hour
        min = time.minute
        sec = time.second
        msec = int(time.microsecond/1000)
        evla = value.origins[0].latitude
        evlo = value.origins[0].longitude
        evdp = value.origins[0].depth/1000

        pandas_list.append([index, eid, year, month, day,
                            hr, min, sec, msec, evla, evlo, evdp])

    df = pd.DataFrame(pandas_list, columns=[
                      "index", "eid", "year", "month", "day", "hr", "min", "sec", "msec", "evla", "evlo", "evdp"])
    df.to_csv("list_284evts_info_my_inversion", sep=" ", index=False)


if __name__ == "__main__":
    main()
