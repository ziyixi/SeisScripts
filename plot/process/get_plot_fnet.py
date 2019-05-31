import numpy as np

url = "../data/fnet.stations"

data = np.loadtxt(url, dtype=np.str)
with open("../data/fnet_plot", "w") as f:
    for row in data:
        f.write(f"{row[3]} {row[2]} {row[0]} \n")
