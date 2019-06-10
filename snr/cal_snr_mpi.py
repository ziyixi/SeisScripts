from glob import glob
from os.path import join

import click
import numpy as np
import obspy
import pandas as pd
import sh
from loguru import logger
from mpi4py import MPI
from obspy.taup import TauPyModel

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def get_dirs(processedurl):
    processedurl = "/mnt/research/seismolab2/japan_slab/data/upload_temp_ziyi/extract_cea/extract/processed"
    search_urls = join(processedurl, "*")
    return glob(search_urls)


def calarrival(wave, model):
    plot_arrivals = {
        "first_p": None,
        "first_s": None
    }
    arrivals = model.get_travel_times(
        source_depth_in_km=wave.stats.sac.evdp, distance_in_degree=wave.stats.sac.gcarc)
    for arrival in arrivals:
        if((arrival.name == 'p') or (arrival.name == "P")):
            plot_arrivals["first_p"] = arrival.time
            break

    for arrival in arrivals:
        if((arrival.name == 's') or (arrival.name == "S")):
            plot_arrivals["first_s"] = arrival.time
            break

    return plot_arrivals


def calsnr(st, starttime, parrival, sarrival):
    st.filter("bandpass", freqmin=1/100, freqmax=1/10)
    noise = st.slice(starttime, parrival)
    signal = st.slice(parrival, sarrival)

    pn = np.sum(noise.data**2)/noise.stats.npts
    ps = np.sum(signal.data**2)/signal.stats.npts

    snr = 10*np.log10((ps-pn)/pn)
    return snr


def maincal(search_urls):
    cal_search_urls = np.array_split(search_urls, size)[rank]
    proc_result_list = []
    model = TauPyModel(model="ak135")
    for cal_search_url in cal_search_urls:
        wave_urls = glob(join(cal_search_url, "*Z"))
        print(wave_urls)
        for wave_url in wave_urls:
            fname = wave_url.split("/")[-1].split(".")
            try:
                wave = obspy.read(wave_url)[0]
            except:
                logger.error(f"[{rank}] handle url: {wave_url}, snr: {np.nan}")
                proc_result_list.append({"event": cal_search_url.split(
                    "/"), "province": fname[0], "station": fname[1], "url": wave_url, "snr": np.nan})
                continue
            plot_arrivals = calarrival(wave, model)
            snr = calsnr(wave, wave.stats.starttime+wave.stats.sac.o, wave.stats.starttime+wave.stats.sac.o +
                         plot_arrivals["first_p"], wave.stats.starttime+wave.stats.sac.o+plot_arrivals["first_s"])
            logger.info(f"[{rank}] handle url: {wave_url}, snr: {snr}")
            proc_result_list.append({"event": cal_search_url.split(
                "/")[-1], "province": fname[0], "station": fname[1], "url": wave_url, "snr": snr})
    return proc_result_list


@click.command()
@click.option('--processedurl', required=True, help="the working directory", type=str)
def main(processedurl):
    sh.mkdir("-p", "./mpilog/")
    logger.add(f"./mpilog/{rank}.log",
               format="{time} {level} {message}",  level="INFO", enqueue=True)

    search_urls = get_dirs(processedurl)
    proc_result_list = maincal(search_urls)
    logger.success(f"[{rank}] finished!")
    comm.Barrier()
    proc_result_list = comm.gather(proc_result_list, root=0)
    if(rank == 0):
        final_result_list = []
        for i in range(size):
            final_result_list = final_result_list+proc_result_list[i]
        final_result = pd.DataFrame(final_result_list)
        final_result.to_pickle("./snr.pkl")


if __name__ == "__main__":
    main()
