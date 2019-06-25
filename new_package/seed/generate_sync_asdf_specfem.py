"""
generate sync asdf file from a Specfem3D directory. Just read in all the sac files and eventxml file.
"""
from os.path import join
import obspy
import pyasdf


def convert_sync_to_asdf(specfem_directory, output_path, with_mpi):
    sync_directory = join(specfem_directory, "OUTPUT_FILES")
    cmt_file = join(specfem_directory, "DATA", "CMTSOLUTION")

    # generate asdf file
    if(not with_mpi):
        ds = pyasdf.ASDFDataSet(output_path, compression="gzip-3")
        print("not with mpi, use gzip-3")
    else:
        ds = pyasdf.ASDFDataSet(output_path, compression=None)
        print("will use mpi, no compression")

    # readin eventxml
    event_xml = obspy.read_events(cmt_file)

    # add event xml to ds
    print(f"adding event_xml {cmt_file}")
    ds.add_quakeml(event_xml)
    event = ds.events[0]

    # readin waves
    print(f"adding waves in {sync_directory}")
    waveform_stream = obspy.read(join(sync_directory, "*.sem.sac"))
    ds.add_waveforms(waveform_stream, tag="sync", event_id=event)

    del ds
    print(f"success in creating {output_path}")


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--specfem_directory', required=True, type=str, help="the used specfem directory")
    @click.option('--output_path', required=True, type=str, help="the output file path")
    @click.option('--with_mpi/--no-with_mpi', default=False, help="if this file will be used with mpi (compression or not)")
    def main(specfem_directory, output_path, with_mpi):
        convert_sync_to_asdf(specfem_directory, output_path, with_mpi)

    main()
