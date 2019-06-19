import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import click
from spherical_geometry.polygon import SphericalPolygon

lon = [91.3320117152011, 74.6060844556399,
       174.409435753150, 144.284491292185, 91.3320117152011]
lat = [9.37366242174489, 61.1396992149365,
       48.6744705245903, 2.08633373396527, 9.37366242174489]
coordinate = []
for i, j in zip(lon, lat):
    phi = np.deg2rad(i)
    theta = np.deg2rad(90-j)
    x = np.sin(theta)*np.cos(phi)
    y = np.sin(theta)*np.sin(phi)
    z = np.cos(theta)
    coordinate.append((x, y, z))
sp = SphericalPolygon(coordinate)


def prepare_data(data_pd, parameter):
    lon_set = set(data_pd["lon"])
    lat_set = set(data_pd["lat"])
    dep_set = set(data_pd["dep"])

    lon_list = sorted(lon_set)
    lat_list = sorted(lat_set)
    dep_list = sorted(dep_set)

    lon_mesh, lat_mesh, dep_mesh = np.meshgrid(lon_list, lat_list, dep_list)
    dx, dy, dz = np.shape(lon_mesh)
    value_mesh = np.zeros_like(lon_mesh)
    x_mesh = np.zeros_like(lon_mesh)
    y_mesh = np.zeros_like(lon_mesh)
    z_mesh = np.zeros_like(lon_mesh)
    r_mesh = np.zeros_like(lon_mesh)

    for i in range(dx):
        for j in range(dy):
            for k in range(dz):
                x_mesh[i, j, k], y_mesh[i, j, k], z_mesh[i, j, k], r_mesh[i, j, k] = lld2xyzr(
                    lat_mesh[i, j, k], lon_mesh[i, j, k], dep_mesh[i, j, k])

    x_mesh_projection = x_mesh/r_mesh  # rmesh couldn't be 0
    y_mesh_projection = y_mesh/r_mesh
    z_mesh_projection = z_mesh/r_mesh

    # get value_mesh
    for i in range(dx):
        for j in range(dy):
            for k in range(dz):
                projected_x = x_mesh_projection[i, j, k]
                projected_y = y_mesh_projection[i, j, k]
                projected_z = z_mesh_projection[i, j, k]
                if(sp.contains_point(projected_x, projected_y, projected_z)):
                    value_mesh[i, j, k] = get_value(
                        data_pd, lat_mesh[i, j, k], lon_mesh[i, j, k], dep_mesh[i, j, k])
                else:
                    value_mesh[i, j, k] = np.nan
    return x_mesh_projection, y_mesh_projection, z_mesh_projection, value_mesh


def lld2xyzr(lat, lon, dep):
    R_EARTH_KM = 6371.0
    r = (R_EARTH_KM-dep)/R_EARTH_KM
    theta = 90-lat
    phi = lon

    z = r*cosd(theta)
    h = r*sind(theta)
    x = h*cosd(phi)
    y = h*sind(phi)

    return (x, y, z, r)


def cosd(x):
    return np.cos(np.deg2rad(x))


def sind(x):
    return np.sin(np.deg2rad(x))
