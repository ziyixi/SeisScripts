import sh
from glob import glob
import click
from os.path import join


def process(main_path):
    events = glob(join(main_path, "*"))
    dirlist = [item.split("/")[-1].split(".")[0] for item in events]
    for item in dirlist:
        sh.mkdir("-p", join(main_path, item))
        sh.mv(join(main_path, f"{item}.seed"),
              join(main_path, item))


@click.command()
@click.option("--main_path", required=True, help="the data directory", type=str)
def main(main_path):
    process(main_path)


if __name__ == "__main__":
    main()
