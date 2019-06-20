import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import click
import numba


def prepare_data(data_pd, parameter):
    lon_set = set(data_pd["lon"])
    lat_set = set(data_pd["lat"])
    dep_set = set(data_pd["dep"])

    lon_list = sorted(lon_set)
    lat_list = sorted(lat_set)
    dep_list = sorted(dep_set)

    lon_mesh, lat_mesh, dep_mesh = np.meshgrid(
        lon_list, lat_list, dep_list, indexing="ij")
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

    for index, row in data_pd.iterrows():
        i = int(round((row.lon-lon_list[0])/(lon_list[1]-lon_list[0]), 0))
        j = int(round((row.lat-lat_list[0])/(lat_list[1]-lat_list[0]), 0))
        k = int(round((row.dep-dep_list[0])/(dep_list[1]-dep_list[0]), 0))
        value_mesh[i, j, k] = row[parameter]

    return x_mesh, y_mesh, z_mesh, value_mesh


def get_value(data_pd, lat, lon, dep, parameter):
    return data_pd.loc[(data_pd.lat == lat) & (data_pd.lon == lon) & (data_pd.dep == dep)][parameter].values[0]


@numba.njit()
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


@numba.njit()
def cosd(x):
    return np.cos(np.deg2rad(x))


@numba.njit()
def sind(x):
    return np.sin(np.deg2rad(x))


# def get_value_func(x_mesh, y_mesh, z_mesh, value_mesh):
#     value_func = RegularGridInterpolator(
#         (x_mesh, y_mesh, z_mesh), value_mesh, method="nearest")
#     return value_func


@numba.njit()
def interp_value(lat, lon, dep, x_mesh, y_mesh, z_mesh, value_mesh):
    x, y, z, _ = lld2xyzr(lat, lon, dep)
    distance2 = (x_mesh-x)**2+(y_mesh-y)**2+(z_mesh-z)**2
    mindistance2 = np.min(distance2)
    coors = np.where(distance2 == mindistance2)
    value = value_mesh[coors[0][0], coors[1][0], coors[2][0]]
    return value


def generate_vertical_profile_grids(lon_list, lat_list, dep_list, hnpts, vnpts):
    lons = np.linspace(lon_list[0], lon_list[1], hnpts)
    lats = np.linspace(lat_list[0], lat_list[1], hnpts)
    deps = np.linspace(dep_list[0], dep_list[1], vnpts)
    return lons, lats, deps


@click.command()
@click.option('--lon1', required=True, type=float, help="lon1")
@click.option('--lon2', required=True, type=float, help="lon2")
@click.option('--lat1', required=True, type=float, help="lat1")
@click.option('--lat2', required=True, type=float, help="lat2")
@click.option('--dep1', required=True, type=float, help="dep1")
@click.option('--dep2', required=True, type=float, help="dep2")
@click.option('--data', required=True, type=str, help="the pickle file")
@click.option('--parameter', required=True, type=str, help="physicial parameter to plot")
@click.option('--hnpts', required=True, type=int, help="horizontal npts")
@click.option('--vnpts', required=True, type=int, help="vertical npts")
def main(lon1, lon2, lat1, lat2, dep1, dep2, data, parameter, hnpts, vnpts):
    lon_list = [lon1, lon2]
    lat_list = [lat1, lat2]
    dep_list = [dep1, dep2]
    data_pd_raw = pd.read_pickle(data)

    # data_pd is too big
    minlon = min(lon1, lon2)
    maxlon = max(lon1, lon2)
    minlat = min(lat1, lat2)
    maxlat = max(lat1, lat2)
    mindep = min(dep1, dep2)
    maxdep = max(dep1, dep2)
    data_pd = data_pd_raw.loc[(data_pd_raw.lat <= maxlat) & (
        data_pd_raw.lat >= minlat) & (data_pd_raw.lon < maxlon) & (data_pd_raw.lon > minlon) & (data_pd_raw.dep >= mindep) & (data_pd_raw.dep <= maxdep)]

    x_mesh, y_mesh, z_mesh, value_mesh = prepare_data(data_pd, parameter)
    lons_plot, lats_plot, deps_plot = generate_vertical_profile_grids(
        lon_list, lat_list, dep_list, hnpts, vnpts)
    values = np.zeros((hnpts, vnpts))
    for ih in range(hnpts):
        for iv in range(vnpts):
            values[ih, iv] = interp_value(
                lats_plot[ih], lons_plot[ih], deps_plot[iv], x_mesh, y_mesh, z_mesh, value_mesh)
            # print(lats_plot[ih], lons_plot[ih], deps_plot[iv], values[ih, iv])

    # plotting part
    plt.figure()
    mesh_plot_lat, mesh_plot_dep = np.meshgrid(
        lats_plot,  deps_plot, indexing="ij")

    # get vmin and vmax
    vmin_round = round(np.min(values), 2)
    if(vmin_round < np.min(values)):
        vmin = vmin_round
    else:
        vmin = vmin_round-0.01
    vmax_round = round(np.max(values), 2)
    if(vmax_round > np.max(values)):
        vmax = vmax_round
    else:
        vmax = vmax_round+0.01
    print(vmin, vmax, np.max(values), np.min(values), vmin_round, vmax_round)
    plt.contourf(mesh_plot_lat, mesh_plot_dep,
                 values,  101, cmap=plt.cm.seismic_r)
    v = np.arange(vmin, vmax, 0.01)
    plt.colorbar(ticks=v, label="perturbation")
    plt.gca().invert_yaxis()
    plt.xlabel(
        f"latitude(°) between (lon: {lon1}°, lat: {lat1}°) and (lon: {lon2}°, lat: {lat2}°)")
    plt.ylabel("depth(km)")
    plt.show()


if __name__ == "__main__":
    main()
