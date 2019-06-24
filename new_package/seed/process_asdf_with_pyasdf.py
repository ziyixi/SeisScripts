from os.path import join

import numpy as np
import obspy
import pyasdf
from loguru import logger
from obspy.geodetics.base import gps2dist_azimuth
from pyasdf import ASDFDataSet

# global parameters
rank = None
size = None


def process_single_event(min_periods, max_periods, asdf_filename, waveform_length, sampling_rate, output_directory, logfile):
    # with pyasdf.ASDFDataSet(asdf_filename) as ds:
    ds = pyasdf.ASDFDataSet(asdf_filename)

    # add logger information
    global rank
    global size
    rank = ds.mpi.comm.Get_rank()
    size = ds.mpi.comm.Get_size()
    isroot = (rank == 0)
    logger.add(logfile, format="{time} {level} {message}", level="INFO")

    # some parameters
    event = ds.events[0]
    origin = event.preferred_origin() or event.origins[0]
    event_time = origin.time
    event_latitude = origin.latitude
    event_longitude = origin.longitude

    for min_period, max_period in zip(min_periods, max_periods):
        # log
        if(isroot):
            logger.success(
                f"[{rank}/{size}] start to process {asdf_filename} from {min_period}s to {max_period}s")

        f2 = 1.0 / max_period
        f3 = 1.0 / min_period
        f1 = 0.8 * f2
        f4 = 1.2 * f3
        pre_filt = (f1, f2, f3, f4)

        # log
        if(isroot):
            logger.success(
                f"[{rank}/{size}] {asdf_filename} is filtered with {f1} {f2} {f3} {f4}")

        def process_function(st, inv):
            # log
            logger.info(
                f"[{rank}/{size}] processing {inv.get_contents()['stations'][0]}")

            # overlap the previous trace
            status_code = check_st_numberlap(st, inv)
            if(status_code == -1):
                return
            elif(status_code == 0):
                pass
            elif(status_code == 1):
                st.merge(method=1, fill_value=0, interpolation_samples=0)
            else:
                raise Exception("unknown status code")

            st.trim(event_time, event_time+waveform_length)

            st.detrend("linear")
            st.detrend("demean")
            st.taper(max_percentage=0.05, type="hann")

            st.remove_response(output="DISP", pre_filt=pre_filt, zero_mean=False,
                               taper=False, inventory=inv)

            # this is not included by Dr. Chen's script
            st.detrend("linear")
            st.detrend("demean")
            st.taper(max_percentage=0.05, type="hann")

            st.interpolate(sampling_rate=sampling_rate)

            station_latitude = inv[0][0].latitude
            station_longitude = inv[0][0].longitude

            _, baz, _ = gps2dist_azimuth(station_latitude, station_longitude,
                                         event_latitude, event_longitude)

            components = [tr.stats.channel[-1] for tr in st]
            if "N" in components and "E" in components:
                st.rotate(method="NE->RT", back_azimuth=baz, inventory=inv)
            else:
                logger.info(
                    f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has problem in rotation")
                return

            # Convert to single precision to save space.
            for tr in st:
                tr.data = np.require(tr.data, dtype="float32")

            return st

        tag_name = "preprocessed_%is_to_%is" % (
            int(min_period), int(max_period))
        tag_map = {
            "raw": tag_name
        }

        ds.process(process_function, join(
            output_directory, tag_name + ".h5"), tag_map=tag_map)
        logger.success(
            f"[{rank}/{size}] success in processing {asdf_filename} from {min_period}s to {max_period}s")

    del ds


def check_st_numberlap(st, inv):
    """
    detect overlapping
    """
    if(len(st) == 0):
        logger.info(
            f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has only 0 traces")
        return -1
    elif(len(st) < 3):
        logger.info(
            f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has less than 3 traces")
        return -1
    elif(len(st) == 3):
        channel_set = set()
        for item in st:
            channel_set.add(item.id[-1])
        if(len(channel_set) == 3):
            return 0
        else:
            logger.info(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has less than 3 channels")
            return -1
    else:
        channel_set = set()
        for item in st:
            channel_set.add(item.id[-1])
        if(len(channel_set) == 3):
            logger.info(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has {len(st)} traces, need to merge")
            return 1
        elif(len(channel_set) < 3):
            logger.info(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has less than 3 channels")
            return -1
        else:
            logger.info(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has {len(channel_set)} channels, error!")
            return -1


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--min_periods', required=True, type=str, help="min periods in seconds, eg: 10,40")
    @click.option('--max_periods', required=True, type=str, help="max periods in seconds, eg: 120,120")
    @click.option('--asdf_filename', required=True, type=str, help="asdf raw data file name")
    @click.option('--waveform_length', required=True, type=float, help="waveform length to cut (from event start time)")
    @click.option('--sampling_rate', required=True, type=int, help="sampling rate in HZ")
    @click.option('--output_directory', required=True, type=str, help="output directory")
    @click.option('--logfile', required=True, type=str, help="the logging file")
    def main(min_periods, max_periods, asdf_filename, waveform_length, sampling_rate, output_directory, logfile):
        min_periods = [float(item) for item in min_periods.split(",")]
        max_periods = [float(item) for item in max_periods.split(",")]
        process_single_event(min_periods, max_periods, asdf_filename,
                             waveform_length, sampling_rate, output_directory, logfile)

    main()
