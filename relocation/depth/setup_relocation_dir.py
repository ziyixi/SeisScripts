"""
setup earthquake depth relocation directory
"""

import obspy
import sh
import numpy as np
import click
from os.path import join
from glob import glob
import copy


def generate_new_cmtsolution_files(cmts_dir, generated_cmts_dir, depth_perturbation_list):
    cmt_names = glob(join(cmts_dir, "*"))
    for cmt_file in cmt_names:
        event = obspy.read_events(cmt_file)[0]
        # gcmt_id = event.resource_id.id.split("/")[-2]
        # there are some problems in changing names
        gcmt_id = cmt_file.split("/")[-1]

        # assume dirs like f"{generated_cmts_dir}/d-3" have already been created
        for depth_per in depth_perturbation_list:
            generated_name = join(generated_cmts_dir, f"d{depth_per}", gcmt_id)
            # there are always problem in copy event, so here I'd like to read in the event again
            event_this_depth = obspy.read_events(cmt_file)[0]
            # event_this_depth = event.copy()
            event_this_depth.origins[0].depth += 1000.0*depth_per
            print(generated_name, generated_cmts_dir, f"d{depth_per}", gcmt_id)
            event_this_depth.write(generated_name, format="CMTSOLUTION")


def setup_basic_structure(main_dir, ref_dir, cmts_dir, depth_perturbation_list):
    # main
    sh.mkdir("-p", main_dir)

    # ref
    sh.cp("-r", ref_dir, join(main_dir, "ref"))

    # refine the structure in ref
    sh.rm("-rf", join(main_dir, "ref", "DATABASES_MPI"))
    sh.rm("-rf", join(main_dir, "ref", "EXAMPLES"))
    sh.rm("-rf", join(main_dir, "ref", "OUTPUT_FILES"))
    sh.rm("-rf", join(main_dir, "ref", "doc"))
    sh.rm("-rf", join(main_dir, "ref", "tests"))

    # mv DATA and utils to upper level
    sh.mv(join(main_dir, "ref", "DATA"), main_dir)
    sh.mv(join(main_dir, "ref", "utils"), main_dir)

    # cmts
    sh.mkdir("-p", join(main_dir, "cmts"))
    sh.cp("-r", cmts_dir, join(main_dir, "cmts", "cmts_raw"))
    sh.mkdir("-p", join(main_dir, "cmts", "cmts_generated"))
    for depth_per in depth_perturbation_list:
        sh.mkdir("-p", join(main_dir, "cmts",
                            "cmts_generated", f"d{depth_per}"))

    # working directory
    sh.mkdir("-p", join(main_dir, "work"))


def setup_structure_after_generat_cmts(main_dir, output_dir, depth_perturbation_list):
    # get cmts names
    cmt_dirs = glob(join(main_dir, "cmts", "cmts_raw", "*"))
    cmt_names = [item.split("/")[-1] for item in cmt_dirs]

    # mkdirs
    for cmt_name in cmt_names:
        sh.mkdir(join(main_dir, "work", cmt_name))
        for depth_per in depth_perturbation_list:
            # sh.mkdir(join(main_dir, "work", cmt_name, f"d{depth_per}"))
            # cp ref to working dirs
            sh.cp("-r", join(main_dir, "ref"),
                  join(main_dir, "work", cmt_name, f"d{depth_per}"))

    # mv DATA and utils back to ref
    sh.mv(join(main_dir, "DATA"), join(main_dir, "ref", "DATA"))
    sh.mv(join(main_dir, "utils"), join(main_dir, "ref", "utils"))

    # mkdir DATA in work directory
    for cmt_name in cmt_names:
        for depth_per in depth_perturbation_list:
            sh.mkdir(join(main_dir, "work", cmt_name, f"d{depth_per}", "DATA"))

    # cp and ln files in DATA
    toln = ["cemRequest", "crust1.0", "crust2.0",
            "crustmap", "epcrust", "eucrust-07", "GLL", "heterogen", "Lebedev_sea99", "Montagner_model", "old", "PPM", "QRFSI12", "s20rts", "s362ani", "s40rts", "Simons_model", "topo_bathy", "Zhao_JP_model"]
    for cmt_name in cmt_names:
        for depth_per in depth_perturbation_list:
            sh.cp(join(main_dir, "cmts", "cmts_generated",
                       f"d{depth_per}", cmt_name), join(main_dir, "work", cmt_name, f"d{depth_per}", "DATA", "CMTSOLUTION"))
            sh.cp(join(main_dir, "ref", "DATA", "Par_file"), join(
                main_dir, "work", cmt_name, f"d{depth_per}", "DATA", "Par_file"))
            sh.cp(join(main_dir, "ref", "DATA", "STATIONS"), join(
                main_dir, "work", cmt_name, f"d{depth_per}", "DATA", "STATIONS"))
            for lnfile in toln:
                sh.ln("-s", join(main_dir, "ref", "DATA", lnfile), join(
                    main_dir, "work", cmt_name, f"d{depth_per}", "DATA", lnfile))

            # ln in work files
            toln_work = ["utils"]
            for lnfile in toln_work:
                sh.ln("-s", join(main_dir, "ref", lnfile), join(
                    main_dir, "work", cmt_name, f"d{depth_per}", lnfile))

    # mkdir and ln DATABASE_MPI and OUTPUT_FILES
    sh.mkdir("-p", output_dir)
    sh.mkdir("-p", join(output_dir, "DATABASES_MPI"))
    sh.mkdir("-p", join(output_dir, "OUTPUT_FILES"))
    for cmt_name in cmt_names:
        for depth_per in depth_perturbation_list:
            sh.mkdir("-p", join(output_dir, "DATABASES_MPI",
                                cmt_name, f"d{depth_per}"))
            sh.mkdir("-p", join(output_dir, "OUTPUT_FILES",
                                cmt_name, f"d{depth_per}"))
            sh.ln("-s", join(output_dir, "DATABASES_MPI",
                             cmt_name, f"d{depth_per}"), join(main_dir, "work", cmt_name, f"d{depth_per}", "DATABASES_MPI"))
            sh.ln("-s", join(output_dir, "OUTPUT_FILES",
                             cmt_name, f"d{depth_per}"), join(main_dir, "work", cmt_name, f"d{depth_per}", "OUTPUT_FILES"))


@click.command()
@click.option('--main_dir', required=True, help="the main working directory", type=str)
@click.option('--output_dir', required=True, help="the output directory in scratch", type=str)
@click.option('--ref_dir', required=True, help="the reference specfem directory", type=str)
@click.option('--cmts_dir', required=True, help="the cmt solution directory", type=str)
@click.option('--depth_perturbation', required=True, help="the depth perturbation, use somthing like -3,-1,5 (in km)", type=str)
def main(main_dir, output_dir, ref_dir, cmts_dir, depth_perturbation):
    depth_perturbation_list = [float(item)
                               for item in depth_perturbation.split(",")]
    setup_basic_structure(main_dir, ref_dir, cmts_dir, depth_perturbation_list)
    generated_cmts_dir = join(main_dir, "cmts", "cmts_generated")
    working_cmts_dir = join(main_dir, "cmts", "cmts_raw")
    generate_new_cmtsolution_files(
        working_cmts_dir, generated_cmts_dir, depth_perturbation_list)
    setup_structure_after_generat_cmts(
        main_dir, output_dir, depth_perturbation_list)


if __name__ == "__main__":
    main()
