"""
get network list from an obspyDMT directory
"""
import click
import pandas as pd
from os.path import join
from glob import glob


@click.command()
@click.option('--main_path', required=True, help="the working directory", type=str)
def get_networks(main_path):
    avaliable_path = glob(
        join(main_path, "data", "*", "*", "info", "availability.txt"))
    result = set()
    for item in avaliable_path:
        data = pd.read_csv(item, names=[
                           "network", "station", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        result = result | set(data.network)

    with open("networks.log", "w") as f:
        for item in sorted(list(result)):
            f.write(f"{item}\n")


if __name__ == "__main__":
    get_networks()
