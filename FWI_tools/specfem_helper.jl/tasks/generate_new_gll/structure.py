import argparse
import sys
from glob import glob
from os.path import join

import numpy as np
import sh


def get_args(args=None):
    parser = argparse.ArgumentParser(
        description='A python script to init the structure of the specfem forward simulation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--wbase',
                        help='work directory base',
                        required=True)

    parser.add_argument('--sbase',
                        help='scratch directory base',
                        required=True)

    parser.add_argument('--specfem',
                        help='specfem directory',
                        required=True)

    parser.add_argument('--taogll',
                        help='tao init gll',
                        required=True)

    parser.add_argument('--mingll',
                        help='min init gll',
                        required=True)

    results = parser.parse_args(args)
    # return results["base"], results["cmtfiles"], results["ref"], results["output"]
    return results.wbase, results.sbase, results.specfem, results.taogll, results.mingll


def setup_structure(wbase, sbase, specfem, taogll, mingll):
    # * sbase
    sh.mkdir("-p", sbase)
    sh.mv(specfem, join(sbase, "specfem"))
    sh.mkdir("-p", join(sbase, "perturbation"))
    per_dirs = ["per_tao", "per_min", "per_ak135_bad",
                "per_ak135_bad_min", "per_ak135_bad_min_tao", "per_ak135_bad_min_tao_smooth"]
    for eachdir in per_dirs:
        sh.mkdir("-p", join(sbase, "perturbation", eachdir))

    # * wbase
    sh.mkdir("-p", wbase)
    sh.ln("-s", join(sbase, "specfem"), join(wbase, "specfem"))
    sh.ln("-s", join(sbase, "perturbation"), join(wbase, "perturbation"))

    sh.mkdir("-p", join(wbase, "model"))
    sh.mkdir("-p", join(wbase, "model", "ak135_good_min_tao"))
    sh.mkdir("-p", join(wbase, "model", "ak135_good_min_tao_smooth"))
    sh.ln("-s", taogll, join(wbase, "model", "tao_gll"))
    sh.ln("-s", mingll, join(wbase, "model", "min_gll"))
    sh.ln("-s", join(wbase, "specfem", "tao", "DATABASES_MPI"),
          join(wbase, "model", "ak135_tao_gll"))
    sh.ln("-s", join(wbase, "specfem", "min", "DATABASES_MPI"),
          join(wbase, "model", "ak135_min_gll"))
    sh.ln("-s", join(wbase, "specfem", "ak135_bad", "DATABASES_MPI"),
          join(wbase, "model", "ak135_bad_gll"))
    sh.ln("-s", join(wbase, "specfem", "ak135_good", "DATABASES_MPI"),
          join(wbase, "model", "ak135_good_gll"))

    sh.mkdir("-p", join(wbase, "control_file"))
    sh.ln("-s", join(wbase, "specfem", "ak135_bad", "DATABASES_MPI"),
          join(wbase, "control_file", "ak135_bad"))
    sh.ln("-s", join(wbase, "specfem", "min", "DATABASES_MPI"),
          join(wbase, "control_file", "min"))
    sh.ln("-s", join(wbase, "specfem", "tao", "DATABASES_MPI"),
          join(wbase, "control_file", "tao"))


if __name__ == "__main__":
    wbase, sbase, specfem, taogll, mingll = get_args(sys.argv[1:])
    setup_structure(wbase, sbase, specfem, taogll, mingll)
