import pandas as pd
from spherical_geometry.polygon import SphericalPolygon
import numpy as np

lon = [91.3320117152011, 74.6060844556399,
       174.409435753150, 144.284491292185, 91.3320117152011]
lat = [9.37366242174489, 61.1396992149365,
       48.6744705245903, 2.08633373396527, 9.37366242174489]
coordinate = []
for i, j in zip(lon, lat):
    phi = np.deg2rad(i)
    theta = np.deg2rad(90-j)
    x = np.sin(theta)*np.cos(phi)
    y = np.sin(theta)*np.sin(phi)
    z = np.cos(theta)
    coordinate.append((x, y, z))
sp = SphericalPolygon(coordinate)


def filter_in_box(row):
    lat = row.evla
    lon = row.evlo
    phi = np.deg2rad(lon)
    theta = np.deg2rad(90-lat)
    x = np.sin(theta)*np.cos(phi)
    y = np.sin(theta)*np.sin(phi)
    z = np.cos(theta)
    return sp.contains_point((x, y, z))


def main():
    data = pd.read_csv(
        "./data/list_227evts_info_EARA2014_inversion", sep="\s+")
    data_selected = data[data.apply(filter_in_box, axis=1)]
    data_selected.to_csv(
        "./data/list_227evts_info_EARA2014_inversion.selected", sep=" ", index=False)


if __name__ == "__main__":
    main()
