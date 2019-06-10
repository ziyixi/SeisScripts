import pandas as pd
# pd.set_option('display.height', 500)
pd.set_option('display.max_rows', 500)

events = pd.read_pickle("../data/event_info.pkl")

print(events[(35 <= events.lat) & (events.lat <= 45)
             & (events.lon >= 135) & (events.lon <= 145)])
