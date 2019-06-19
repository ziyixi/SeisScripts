import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import click
from spherical_geometry.polygon import SphericalPolygon


def prepare_data(data_pd, parameter):
    lon_set = set(data_pd["lon"])
    lat_set = set(data_pd["lat"])
    dep_set = set(data_pd["dep"])

    lon_list = sorted(lon_set)
    lat_list = sorted(lat_set)
    dep_list = sorted(dep_set)

    lon_mesh, lat_mesh, dep_mesh = np.meshgrid(lon_list, lat_list, dep_list)
    dx, dy, dz = np.shape(lon_mesh)
    value = np.zeros_like(lon_mesh)
    x_mesh = np.zeros_like(lon_mesh)
    y_mesh = np.zeros_like(lon_mesh)
    z_mesh = np.zeros_like(lon_mesh)

    for i in range(dx):
        for j in range(dy):
            for k in range(dz):
                x_mesh[i, j, k], y_mesh[i, j, k], z_mesh[i, j, k] = lld2xyz(
                    lat_mesh[i, j, k], lon_mesh[i, j, k], dep_mesh[i, j, k])


def lld2xyz(lat, lon, dep):
    R_EARTH_KM = 6371.0
    r = (R_EARTH_KM-dep)/R_EARTH_KM
    theta = 90-lat
    phi = lon

    z = r*cosd(theta)
    h = r*sind(theta)
    x = h*cosd(phi)
    y = h*sind(phi)

    return (x, y, z)


def cosd(x):
    return np.cos(np.deg2rad(x))


def sind(x):
    return np.sin(np.deg2rad(x))
