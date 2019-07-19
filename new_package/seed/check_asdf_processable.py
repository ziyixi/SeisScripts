"""
some sync asdf file may have problem, we should check it.
"""
from glob import glob
import pyasdf
import numpy as np
import click
from os.path import join


def get_all_files(main_dir):
    return glob(join(main_dir, "*h5"))


def check(fname):
    try:
        with pyasdf.ASDFDataSet(fname) as ds:
            for item in ds.waveforms.list():
                maxvalue = np.max(ds.waveforms[item].sync[0].data)
        return True
    except:
        return False


@click.command()
@click.option('--main_dir', required=True, type=str, help="working directory")
def main(main_dir):
    all_files = get_all_files(main_dir)
    for item in all_files:
        status = check(item)
        if(status):
            pass
        else:
            print(item)


if __name__ == "__main__":
    main()
