"""
collect events' information from the directory that have been processed
"""
import pandas as pd
import obspy
import glob
import click


def get_file_paths(basepath):
    events_path = glob.glob(f"{basepath}/*")
    event_lists = []
    for event in events_path:
        total_sac_files = glob.glob(f"{event}/*SAC")
        total_sac_files = sorted(total_sac_files)
        event_lists.append(total_sac_files[0])
    return event_lists


@click.command()
@click.option('--basepath', required=True, help="the data directory", type=str)
def main(basepath):
    event_paths = get_file_paths(basepath)
    df = pd.DataFrame(columns=["id", "snr", "lat", "lon", "mag", "dep"])
    for i, value in enumerate(event_paths):
        thedata = obspy.read(value)[0]
        df.loc[i] = [value.split(
            "/")[-2], 0, thedata.stats.sac.evla, thedata.stats.sac.evlo, thedata.stats.sac.mag, thedata.stats.sac.evdp]
    df.to_pickle("./event.pkl")


if __name__ == "__main__":
    main()
