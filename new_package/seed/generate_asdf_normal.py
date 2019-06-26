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
from obspy.io.xseed import Parser


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
    station_xml = obspy.core.inventory.inventory.Inventory()

    for i, filename in enumerate(files):
        logger.info(f"adding waves #{i} {filename}")
        # try to use obspy
        try:
            waveform_stream = obspy.read(filename)
            logger.info(f"{filename} is able to use obspy to read waveforms")
        except:
            dirpath = tempfile.mkdtemp()
            command = f"rdseed -d -f {filename} -q {dirpath}"
            subprocess.call(command, shell=True)
            waveform_stream = obspy.read(join(dirpath, "*SAC"))
            logger.info(f"{filename} could only use rdseed to read waveforms")

        ds.add_waveforms(waveform_stream, tag="raw", event_id=event)

        # add stationxml (since statinxml may be different for different events, it's better
        # to store only one event in ds)
        logger.info(f"adding stationxml #{i} {filename}")

        try:
            station_xml_file_obj = tempfile.NamedTemporaryFile(delete=False)
            station_xml_file_obj.close()
            station_xml_file_path = station_xml_file_obj.name
            sp = Parser(filename)
            sp.write_xseed(station_xml_file_path)
            station_xml_this_seed = obspy.read_inventory(station_xml_file_path)
            logger.info(f"{filename} could use obspy to read stationxml")
        except:
            dirpath = tempfile.mkdtemp()
            command = f"rdseed -R -f {filename} -q {dirpath}"
            subprocess.call(command, shell=True)

            station_xml_this_seed = obspy.core.inventory.inventory.Inventory()
            allfiles = glob(join(dirpath, "*"))
            for fname in allfiles:
                inv_temp = obspy.read_inventory(fname)
                # update essencial location information
                inv_temp = update_info(inv_temp, waveform_stream)
                if(inv_temp == None):
                    continue
                station_xml_this_seed += inv_temp
            logger.info(f"{filename} could on;y use rdseed to read stationxml")

        station_xml += station_xml_this_seed

    ds.add_stationxml(station_xml)

    del ds
    logger.success(f"success in creating {output_path}")


def update_info(inv, waveform_stream):
    usable_channels = inv.get_contents()["channels"]
    # loop all channels, search info
    status = False
    for channel in usable_channels:  # channel, like BO.NKG..BHE
        if(status == False):
            for thewave in waveform_stream:
                waveid = thewave.id
                if(waveid == channel):
                    status = True
                    inv[0][0].latitude = thewave.stats.sac.stla
                    inv[0][0].longitude = thewave.stats.sac.stlo
                    inv[0][0].elevation = thewave.stats.sac.stel
                    break
    if(not status):
        logger.error(
            f"problem in updating head info for {inv.get_contents()['stations'][0]}")
        return None
    else:
        return inv


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
