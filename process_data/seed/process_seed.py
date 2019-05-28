#!/usr/bin/envv python

import glob
import os
import subprocess

import click
import numpy as np
import sh
from loguru import logger
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
logger.add("process_seed.log", format="{time} {level} {message}",
           filter="process_seed", level="INFO")
os.putenv("SAC_DISPLAY_COPYRIGHT", '0')


def process_seeds(event_paths):
    event_path_this_rank = generate_paths(event_paths)

    # comment as having done this procedure
    logger.info(f"[rank:{rank}] start to rdseed")
    rdseed(event_path_this_rank)

    # logger.info(f"[rank:{rank}] start to merge")
    # merge(event_path_this_rank)

    # logger.info(f"[rank:{rank}] start to rename")
    # rename(event_path_this_rank)

    # logger.info(f"[rank:{rank}] start to transfer")
    # transfer(event_path_this_rank)

    # logger.info(f"[rank:{rank}] start to rotate")
    # rotate(event_path_this_rank)

    logger.success(f"[rank:{rank}] finished!")


def generate_paths(event_paths):
    return np.array_split(event_paths, size)[rank]


def rdseed(event_path_this_rank):
    root_path = str(sh.pwd())[:-1]
    for thedir in event_path_this_rank:
        sh.cd(thedir)
        for seed in glob.glob("*SEED"):
            logger.info(f"[rank:{rank},dir:{thedir}] rdseed {seed}")
            sh.rdseed('-pdf', seed)
        sh.cd(root_path)


def merge(event_path_this_rank):
    root_path = str(sh.pwd())[:-1]
    for thedir in event_path_this_rank:
        sh.cd(thedir)

        sets = {}
        for fname in glob.glob("*.SAC"):
            key = '.'.join(fname.split('.')[6:10])
            if key not in sets:
                sets[key] = 1
            else:
                sets[key] += 1

        # prepare sac command
        stdin_list = []
        stdin_list.append(f"wild echo off \n")
        to_del = []

        for key, value in sets.items():
            if(value == 1):
                continue

            logger.info(
                f"[rank:{rank},dir:{thedir}] merge {key}: {value} traces")
            traces = sorted(glob.glob('.'.join(['*', key, '?', 'SAC'])))
            stdin_list.append(f"r *.{key}.?.SAC \n")
            stdin_list.append(f"merge gap zero overlap average \n")
            stdin_list.append(f"w {traces[0]} \n")

            to_del.extend(traces[1:])

        stdin_list.append(f"q\n")
        sh.sac(_in=stdin_list)

        logger.info(f"[rank:{rank},dir:{thedir}] keep only the master seed")
        for file in to_del:
            sh.rm(file)

        sh.cd(root_path)


def rename(event_path_this_rank):
    root_path = str(sh.pwd())[:-1]
    for thedir in event_path_this_rank:
        sh.cd(thedir)
        for fname in glob.glob("*.SAC"):
            net, sta, loc, chn = fname.split('.')[6:10]
            # logger.info(
            #     f"[rank:{rank},dir:{thedir}] rename {fname} to {net}.{sta}.{loc}.{chn}.SAC")
            sh.mv(fname, f"{net}.{sta}.{loc}.{chn}.SAC")
        sh.cd(root_path)


def transfer(event_path_this_rank):
    root_path = str(sh.pwd())[:-1]
    for thedir in event_path_this_rank:
        sh.cd(thedir)
        stdin_list = []

        for sacfile in glob.glob("*.SAC"):
            net, sta, loc, chn = sacfile.split('.')[0:4]
            pz = glob.glob(f"SAC_PZs_{net}_{sta}_{chn}_{loc}_*_*")

            if(len(pz) != 1):
                logger.error(
                    f"[rank:{rank},dir:{thedir}] error in transfering for {sacfile} in seeking {pz}")
                continue

            # logger.info(
            #     f"[rank:{rank},dir:{thedir}] transfer {sacfile} with {pz}")
            stdin_list.append(f"r {sacfile}\n")
            stdin_list.append(f"rmean; rtr; taper \n")
            stdin_list.append(
                f"trans from pol s {pz[0]} to none freq 0.001 0.005 5 10\n")
            stdin_list.append(f"mul 1.0e9 \n")
            stdin_list.append("w over\n")
        stdin_list.append(f"q\n")
        sh.sac(_in=stdin_list)
        sh.cd(root_path)


def rotate(event_path_this_rank):
    root_path = str(sh.pwd())[:-1]
    for thedir in event_path_this_rank:
        sh.cd(thedir)

        # build the collection of NET.STA.LOC.CH
        sets = set()
        for fname in glob.glob("*.SAC"):
            net, sta, loc, chn = fname.split('.')[0:4]
            key = '.'.join([net, sta, loc, chn[0:2]])
            sets.add(key)

        stdin_list = []
        for key in sets:
            # if Z component exists
            Z = f"{key}Z.SAC"
            if not os.path.exists(Z):
                logger.error(
                    f"[rank:{rank},dir:{thedir}] vertical component missing for {key}")
                continue

            # if horizontal exists
            if os.path.exists(key + "E.SAC") and os.path.exists(key + "N.SAC"):
                E = key + "E.SAC"
                N = key + "N.SAC"
            elif os.path.exists(key + "1.SAC") and os.path.exists(key + "2.SAC"):
                E = key + "1.SAC"
                N = key + "2.SAC"
            else:
                logger.error(
                    f"[rank:{rank},dir:{thedir}] horizontal component missing for {key}")
                continue

            # check if orthogonal
            cmd = 'saclst cmpaz f {}'.format(E).split()
            Ecmpaz = subprocess.check_output(cmd).decode().split()[1]
            cmd = 'saclst cmpaz f {}'.format(N).split()
            Ncmpaz = subprocess.check_output(cmd).decode().split()[1]
            cmpaz_delta = abs(float(Ecmpaz) - float(Ncmpaz))
            if not (abs(cmpaz_delta-90) <= 0.01 or abs(cmpaz_delta-270) <= 0.01):
                logger.error(
                    f"[rank:{rank},dir:{thedir}] {key}: cmpaz1={Ecmpaz}, cmpaz2={Ncmpaz} are not orthogonal!")
                continue

            # check B,E,Delta
            cmd = 'saclst b e delta f {}'.format(Z).split()
            Zb, Ze, Zdelta = subprocess.check_output(cmd).decode().split()[1:]
            cmd = 'saclst b e delta f {}'.format(E).split()
            Eb, Ee, Edelta = subprocess.check_output(cmd).decode().split()[1:]
            cmd = 'saclst b e delta f {}'.format(N).split()
            Nb, Ne, Ndelta = subprocess.check_output(cmd).decode().split()[1:]

            if not (float(Zdelta) == float(Edelta) and float(Zdelta) == float(Ndelta)):
                logger.error(
                    f"[rank:{rank},dir:{thedir}] {key}: {key} delta not equal! ")
                continue

            # get longest data window
            begin = max(float(Zb), float(Eb), float(Nb))
            end = min(float(Ze), float(Ee), float(Ne))

            # output with the form NET.STA.LOC.[RTZ]
            prefix = key[:-2]
            R, T, Z0 = prefix + '.R', prefix + '.T', prefix + '.Z'

            # logger.info(f"[rank:{rank},dir:{thedir}] rotate {key}")
            stdin_list.append(f"cut {begin} {end} \n")
            stdin_list.append(f"r {E} {N} \n")
            stdin_list.append(f"rotate to gcp \n")
            stdin_list.append(f"w {R} {T} \n")
            stdin_list.append(f"r {Z} \n")
            stdin_list.append(f"w {Z0} \n")
        stdin_list.append(f"q \n")
        sh.sac(_in=stdin_list)

        # delete initial files
        for fname in glob.glob("*.SAC"):
            logger.info(
                f"[rank:{rank},dir:{thedir}] delete SAC file for {key}")
            sh.rm(fname)

        sh.cd(root_path)


@click.command()
@click.option('--main_path', required=True, help="the data directory", type=str)
def main(main_path):
    paths = glob.glob(f"{main_path}/*")
    process_seeds(paths)


if __name__ == "__main__":
    main()
