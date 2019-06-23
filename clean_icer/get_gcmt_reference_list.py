import obspy
import glob
import pickle

files = glob.glob("./cmts/*")
result = {}
cea_ids = [item.split("/")[-1] for item in files]
for cea_id, thefile in zip(cea_ids, files):
    event = obspy.read_events(thefile)[0]
    gcmt_id = event.resource_id.id.split("/")[-2]
    result[cea_id] = gcmt_id

pickle.dump(result, open("cmts_ref.pkl", "wb"))
