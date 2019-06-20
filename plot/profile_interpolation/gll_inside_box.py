import pandas as pd
from spherical_geometry.polygon import SphericalPolygon
import numpy as np
import click

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


@click.command()
@click.option('--pickle_file', required=True, type=str)
@click.option('--output_file', required=True, type=str)
def main(pickle_file, output_file):
    data_pd = pd.read_pickle(pickle_file)
    parameter_list = data_pd.columns[3:]

    for index, row in data_pd.iterrows():
        lat = row.lat
        lon = row.lon
        phi = np.deg2rad(lon)
        theta = np.deg2rad(90-lat)
        x = np.sin(theta)*np.cos(phi)
        y = np.sin(theta)*np.sin(phi)
        z = np.cos(theta)
        if(not sp.contains_point((x, y, z))):
            for item in parameter_list:
                data_pd.loc[index, item] = np.nan

    data_pd.to_pickle(output_file)


if __name__ == "__main__":
    main()
