"""
generate asdf file for raw data for a single directory. (SEED files for the same event)
"""
import pyasdf
from glob import glob
import obspy
import tempfile
from os.path import join
from obspy.io.xseed import Parser


def generate_asdf_for_single_event(seed_directory, cmt_path, output_path, with_mpi):
    # generate asdf file
    if(not with_mpi):
        ds = pyasdf.ASDFDataSet(output_path, compression="gzip-3")
        print("not with mpi, use gzip-3")
    else:
        ds = pyasdf.ASDFDataSet(output_path, compression=None)
        print("will use mpi, no compression")

    # generate a tmp file to store stationxml
    station_xml_file_obj = tempfile.NamedTemporaryFile(delete=False)
    station_xml_file_obj.close()
    station_xml_file_path = station_xml_file_obj.name

    # readin eventxml
    event_xml = obspy.read_events(cmt_path)

    # add event xml to ds
    print(f"adding event_xml {cmt_path}")
    ds.add_quakeml(event_xml)
    event = ds.events[0]

    # readin waves
    files = glob(join(seed_directory, "*"))
    for i, filename in enumerate(files):
        print(f"adding waves #{i} {filename}")
        waveform_stream = obspy.read(filename)
        ds.add_waveforms(waveform_stream, tag="raw", event_id=event)

    # add stationxml (since statinxml may be different for different events, it's better
    # to store only one event in ds)
    station_xml = obspy.core.inventory.inventory.Inventory()
    for i, filename in enumerate(files):
        print(f"adding stationxml #{i} {filename}")
        sp = Parser(filename)
        sp.write_xseed(station_xml_file_path)
        station_xml_this_file = obspy.read_inventory(station_xml_file_path)
        station_xml += station_xml_this_file
    ds.add_stationxml(station_xml)
    del ds
    print(f"success in creating {output_path}")


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--seed_directory', required=True, type=str, help="the directory containing all the seed files for this event")
    @click.option('--cmt_path', required=True, type=str, help="the CMTSOLUTION file for this event")
    @click.option('--output_path', required=True, type=str, help="the output path for hdf5 file")
    @click.option('--with_mpi/--no-with_mpi', default=False, help="if this file will be used with mpi (compression or not)")
    def main(seed_directory, cmt_path, output_path, with_mpi):
        generate_asdf_for_single_event(
            seed_directory, cmt_path, output_path, with_mpi)

    main()
