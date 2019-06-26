"""
remove stations that have no data. (discarded for variety of reasons)
"""
import pyasdf
import subprocess
from loguru import logger
import click


def remove_stations(ds):
    waveform_list = ds.waveforms.list()
    for item in waveform_list:
        wg = ds.waveforms[item]
        data_tags = wg.get_waveform_tags()
        if(len(data_tags) == 0):
            inv = wg["StationXML"]
            logger.info(f"remove {inv.get_contents()['stations'][0]}")
            del ds.waveforms[item]


@click.command()
@click.option('--asdf_file', required=True, type=str, help="the data asdf file")
@click.option('--logfile', required=True, type=str, help="the log file")
@click.option('--output_file', required=True, type=str, help="the output file")
def main(asdf_file, logfile, output_file):
    command = f"cp {asdf_file} {output_file}"
    subprocess.call(command, shell=True)

    ds = pyasdf.ASDFDataSet(output_file)
    logger.add(logfile, format="{time} {level} {message}", level="INFO")
    logger.info(f"start to process {output_file}")

    remove_stations(ds)
    logger.success("finish removing missing stations")
