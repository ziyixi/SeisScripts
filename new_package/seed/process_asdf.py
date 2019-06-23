import obspy
import numpy as np
from pyasdf import ASDFDataSet
import pyasdf
from obspy.geodetics.base import gps2dist_azimuth
from os.path import join


def process_single_event(min_periods, max_periods, asdf_filename, waveform_length, sampling_rate, output_directory):
    with pyasdf.ASDFDataSet(asdf_filename) as ds:
        # some parameters
        event = ds.events[0]
        origin = event.preferred_origin() or event.origins[0]
        event_time = origin.time
        event_latitude = origin.latitude
        event_longitude = origin.longitude

        for min_period, max_period in zip(min_periods, max_periods):
            f2 = 1.0 / max_period
            f3 = 1.0 / min_period
            f1 = 0.8 * f2
            f4 = 1.2 * f3
            pre_filt = (f1, f2, f3, f4)

            def process_function(st, inv):
                st.trim(event_time, event_time+waveform_length)

                st.detrend("linear")
                st.detrend("demean")
                st.taper(max_percentage=0.05, type="hann")

                st.remove_response(output="DISP", pre_filt=pre_filt, zero_mean=False,
                                   taper=False)

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
                    st.rotate(method="NE->RT", back_azimuth=baz)
                else:
                    print(
                        f"problem in rotating {st[0].stats.network}.{st[0].stats.station}")

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


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--min_periods', required=True, type=str, help="min periods in seconds, eg: 10,40")
    @click.option('--max_periods', required=True, type=str, help="max periods in seconds, eg: 120,120")
    @click.option('--asdf_filename', required=True, type=str, help="asdf raw data file name")
    @click.option('--waveform_length', required=True, type=float, help="waveform length to cut (from event start time)")
    @click.option('--sampling_rate', required=True, type=int, help="sampling rate in HZ")
    @click.option('--output_directory', required=True, type=str, help="output directory")
    def main(min_periods, max_periods, asdf_filename, waveform_length, sampling_rate, output_directory):
        min_periods = [float(item) for item in min_periods.split(",")]
        max_periods = [float(item) for item in max_periods.split(",")]
        process_single_event(min_periods, max_periods, asdf_filename,
                             waveform_length, sampling_rate, output_directory)

    main()
