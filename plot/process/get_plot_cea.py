import numpy as np

url = "../data/cea.stations"

data = np.loadtxt(url, dtype=np.str)
with open("../data/cea_plot", "w") as f:
    for row in data:
        f.write(f"{row[3]} {row[2]} {row[0]}.{row[1]} \n")
