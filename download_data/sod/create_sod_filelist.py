"""
A script to create SOD file list
"""
import pandas as pd
import obspy
import numpy as np


def main():
    events = obspy.read_events("./event_info.xml")
    df = pd.DataFrame(columns=["time", "latitude", "longitude", "depth", "depthUnits", "magnitude", "magnitudeType",
                               "magnitudeContributor", "catalog", "contributor", "name", "flinnEngdahlRegion", "flinnEngdahlRegionType"])
    for index, item in enumerate(events):
        df.loc[index] = [
            str(item.origins[0].time),
            item.origins[0].latitude,
            item.origins[0].longitude,
            item.origins[0].depth,
            "METER",
            item.magnitudes[0].mag,
            item.magnitudes[0].magnitude_type,
            np.nan,
            np.nan,
            np.nan,
            item.origins[0].region,
            0,
            1
        ]
    df.to_csv("event_info.csv", index=False)


if __name__ == "__main__":
    main()
