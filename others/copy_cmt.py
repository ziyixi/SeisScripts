import pandas as pd
import subprocess

used_events_path = "/mnt/research/seismolab2/japan_slab/cmts/used_events"
cmts_path = "/mnt/research/seismolab2/japan_slab/cmts/EARA2014_inversion"
selected_cmts_path = "/mnt/research/seismolab2/japan_slab/cmts/selected_cmts"

events = pd.read_csv(used_events_path, sep=" ")
cmts_names = events.eid.values

for cmt in cmts_names:
    # sh.cp(f"{cmts_path}/*{cmt}", f"{selected_cmts_path}/")
    subprocess.call(f"cp {cmts_path}/*{cmt} {selected_cmts_path}/", shell=True)
