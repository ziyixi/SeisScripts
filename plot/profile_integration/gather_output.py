"""
gather output files from Julia to get the evenly distributed grid
"""
import pandas as pd
from spherical_geometry.polygon import SphericalPolygon
import numpy as np


def get_pkl(julia_output_dir, nproc):
