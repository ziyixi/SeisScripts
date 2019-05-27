"""
download seed files in IRIS FTP.
"""
from ftplib import FTP
import sh
import click
from os.path import join, isfile, isdir
import numpy as np
from logbook import Logger, FileHandler
from tqdm import tqdm


def get_ftp_file_list(username):
    ftp = FTP("ftp.iris.washington.edu")
    ftp.login()
    ftp.cwd(join("pub", "userdata", username))
    return ftp.nlst()


def get_download_urls(filelist, username):
    urls = []
    baseurl = "ftp://ftp.iris.washington.edu/pub/userdata/" + username + "/"
    for thefile in filelist:
        urls.append(baseurl + thefile)
    return urls


def get_files_to_download(main_directory, filelist_ftp):
    sh.mkdir("-p", main_directory)
    sh.mkdir("-p", join(main_directory, "data"))

    # ftp.filelist
    with open(join(main_directory, "ftp.filelist"), "w") as f:
        for item in filelist_ftp:
            f.write(item + "\n")

    # local.filelist
    if isfile(join(main_directory, "local.filelist")):
        filelist_local = np.loadtxt(
            join(main_directory, "local.filelist"), dtype=np.str
        )
    else:
        filelist_local = np.array([], dtype=np.str)

    filelist_ftp = set(filelist_ftp)
    filelist_local = set(filelist_local)

    filelist_todownload = filelist_ftp - filelist_local

    return filelist_todownload


@click.command()
@click.option(
    "--thread_number",
    required=True,
    help="the thread number to download the data",
    type=int,
)
@click.option(
    "--username", required=True, help="the directory owner's name in ftp", type=str
)
@click.option(
    "--main_directory", required=True, help="the main downloading directory", type=str
)
def main(thread_number, username, main_directory):
    # set up logging
    log_handler = FileHandler(join(main_directory, "log"))
    log_handler.push_application()
    log = Logger("fdsn_log")

    filelist_ftp = get_ftp_file_list(username)
    files_to_download = get_files_to_download(main_directory, filelist_ftp)
    downloading_urls = get_download_urls(files_to_download, username)

    for download_url in tqdm(downloading_urls):
        fname = download_url.split("/")[-1]
        log_message = f"start to download {download_url} "
        log.info(log_message)
        sh.wget("-c", download_url, "-O", join(main_directory, "data", fname))
        log_message = f"finish downloading {download_url} "
        log.info(log_message)
        with open(join(main_directory, "local.filelist"), "a") as file:
            file.write(f'{download_url.split("/")[-1]}\n')

    log.info("success")


if __name__ == "__main__":
    main()
