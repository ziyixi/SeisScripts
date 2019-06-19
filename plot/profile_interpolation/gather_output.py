"""
gather output files from Julia to get the evenly distributed grid
"""
import pandas as pd
from spherical_geometry.polygon import SphericalPolygon
import numpy as np
from os.path import join
import click


def get_pd(julia_output_dir, nproc, parameter_list):
    column_names = ["lon", "lat", "dep"]+parameter_list
    data = pd.DataFrame(columns=column_names)
    for rank in range(int(nproc)):
        readin_name = join(julia_output_dir, str(rank))
        data_this_rank = pd.read_csv(
            readin_name, sep=" ", names=column_names)
        data = data+data_this_rank
    return data


@click.command()
@click.option('--julia_output_dir', required=True, help="the data directory", type=str)
@click.option('--nproc', required=True, help="number of processors have been used", type=str)
@click.option('--parameters', required=True, help="parameters seprated by comma", type=str)
@click.option('--output', required=True, help="the outputed pkl directory", type=str)
def main(julia_output_dir, nproc, parameters, output):
    parameter_list = parameters.split(",")
    data = get_pd(julia_output_dir, nproc, parameter_list)
    data.to_pickle(output)


if __name__ == "__main__":
    main()
