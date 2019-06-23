import os
import glob
import subprocess
import click


@click.command()
@click.option("--processedurl", required=True, help="the data directory", type=str)
@click.option("--seedurl", required=True, help="the directory that will store the seed files", type=str)
@click.option("--sacpzurl", required=True, help="the directory that will store the sacpz files", type=str)
def main(processedurl, seedurl, sacpzurl):
    dirs = glob.glob(processedurl+"/*")
    for dir in dirs:
        fname = dir.split("/")[-1]
        command = "mkdir -p "+seedurl+"/"+fname
        subprocess.call(command, shell=True)
        command = "mkdir -p "+sacpzurl+"/"+fname
        subprocess.call(command, shell=True)
        command = "mv "+dir+"/SAC_PZs* "+sacpzurl+"/"+fname+"/"
        subprocess.call(command, shell=True)
        command = "mv "+dir+"/*SEED "+seedurl+"/"+fname+"/"
        subprocess.call(command, shell=True)


if(__name__ == "__main__"):
    main()
