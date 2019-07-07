import pyasdf
import pickle
import click
import numpy as np


@click.command()
@click.option('--obs_path', required=True, type=str, help="the obs hdf5 file path")
def main(obs_path):
    with open(obs_path+"traveltimes.pkl", 'rb') as handle:
        results = pickle.load(handle)
    with pyasdf.ASDFDataSet(obs_path, mode="a") as obs_ds:
        for item in results:
            print(item)
            obs_ds.add_auxiliary_data(
                np.zeros(1, dtype=np.float), data_type="Traveltimes", path=item.replace(".", "/"), parameters=results[item])


if __name__ == "__main__":
    main()
