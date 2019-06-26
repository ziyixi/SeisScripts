"""
since always obspy may have problem in reading seed files, it's better to use rdseed to generate sac files and resp files.
"""

import pyasdf
from glob import glob
import obspy
import tempfile
from os.path import join
import subprocess
from loguru import logger


def generate_asdf_for_single_event(seed_directory, cmt_path, output_path, with_mpi, logfile):
    logger.add(logfile, format="{time} {level} {message}", level="INFO")
    # generate asdf file
    if(not with_mpi):
        ds = pyasdf.ASDFDataSet(output_path, compression="gzip-3")
        logger.info("not with mpi, use gzip-3")
    else:
        ds = pyasdf.ASDFDataSet(output_path, compression=None)
        logger.info("will use mpi, no compression")

    # readin eventxml
    event_xml = obspy.read_events(cmt_path)

    # add event xml to ds
    logger.info(f"adding event_xml {cmt_path}")
    ds.add_quakeml(event_xml)
    event = ds.events[0]

    # readin waves
    files = glob(join(seed_directory, "*"))
    for i, filename in enumerate(files):
        logger.info(f"adding waves #{i} {filename}")

        # waveform_stream = read_stream(filename)
        dirpath = tempfile.mkdtemp()
        command = f"rdseed -d -f {filename} -q {dirpath}"
        subprocess.call(command, shell=True)
        waveform_stream = obspy.read(join(dirpath, "*SAC"))

        ds.add_waveforms(waveform_stream, tag="raw", event_id=event)

    # add stationxml (since statinxml may be different for different events, it's better
    # to store only one event in ds)
    station_xml = obspy.core.inventory.inventory.Inventory()
    for i, filename in enumerate(files):
        logger.info(f"adding stationxml #{i} {filename}")

        # sp = Parser(filename)
        # sp.write_xseed(station_xml_file_path)
        # station_xml_this_file = obspy.read_inventory(station_xml_file_path)
        dirpath = tempfile.mkdtemp()
        command = f"rdseed -R -f {filename} -q {dirpath}"
        subprocess.call(command, shell=True)

        # station_xml_this_file = obspy.read_inventory(station_xml_file_path)
        # station_xml += station_xml_this_file

        station_xml_this_seed = obspy.core.inventory.inventory.Inventory()
        allfiles = glob(join(dirpath, "*"))
        for fname in allfiles:
            station_xml_this_seed += obspy.read_inventory(fname)

        station_xml += station_xml_this_seed

    ds.add_stationxml(station_xml)
    del ds
    logger.success(f"success in creating {output_path}")


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--seed_directory', required=True, type=str, help="the directory containing all the seed files for this event")
    @click.option('--cmt_path', required=True, type=str, help="the CMTSOLUTION file for this event")
    @click.option('--output_path', required=True, type=str, help="the output path for hdf5 file")
    @click.option('--with_mpi/--no-with_mpi', default=False, help="if this file will be used with mpi (compression or not)")
    @click.option('--logfile', required=True, type=str, help="the log file path")
    def main(seed_directory, cmt_path, output_path, with_mpi, logfile):
        generate_asdf_for_single_event(
            seed_directory, cmt_path, output_path, with_mpi, logfile)

    main()
