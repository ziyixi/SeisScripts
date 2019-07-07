import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt
import obspy
import pyasdf
from obspy.geodetics.base import gps2dist_azimuth, locations2degrees
from obspy.taup import TauPyModel
from recordtype import recordtype
import numpy as np

model = TauPyModel(model='ak135')
to_plot_trace = recordtype("to_plot_trace", ["obs", "syn", "property"])
plotting_order_structure = recordtype("plotting_order_structure",
                                      ["to_plot_traces", "label"])


def get_to_plot_traces_for_each_azimuth_bin(ds_obs, ds_syn, bin_width=15):
    # find stations in common
    obs_stations = set(ds_obs.waveforms.list())
    syn_stations = set(ds_syn.waveforms.list())
    common_stations = obs_stations & syn_stations

    # generate streams
    azimuth_bin_number = 360//bin_width
    azimuth_bins_z = [[]
                      for i in range(azimuth_bin_number)]
    azimuth_bins_r = [[]
                      for i in range(azimuth_bin_number)]
    azimuth_bins_t = [[]
                      for i in range(azimuth_bin_number)]

    # event information
    event = ds_obs.events[0]
    origin = event.preferred_origin() or event.origins[0]
    evla = origin.latitude
    evlo = origin.longitude
    evdp = origin.depth/1000.0

    # calculate some information
    all_azimuth_bins_z = []
    all_azimuth_bins_r = []
    all_azimuth_bins_t = []
    for station_name_item in common_stations:
        obs_tag_this_station = ds_obs.waveforms[station_name_item].get_waveform_tags()[
            0]
        syn_tag_this_station = ds_syn.waveforms[station_name_item].get_waveform_tags()[
            0]

        # streams, in the order of r,t,z
        obs_this_station = ds_obs.waveforms[station_name_item][obs_tag_this_station]
        syn_this_station = ds_syn.waveforms[station_name_item][syn_tag_this_station]

        # get azimuth
        inv_obs = ds_obs.waveforms[station_name_item]["StationXML"]
        stla = inv_obs[0][0].latitude
        stlo = inv_obs[0][0].longitude
        print(station_name_item, stla, stlo, evla, evlo, evdp)
        info_to_store = get_property_times(
            stla, stlo, evla, evlo, evdp)
        to_store_r = to_plot_trace(
            obs_this_station[0], syn_this_station[0], info_to_store)
        to_store_t = to_plot_trace(
            obs_this_station[1], syn_this_station[1], info_to_store)
        to_store_z = to_plot_trace(
            obs_this_station[2], syn_this_station[2], info_to_store)
        all_azimuth_bins_r.append(to_store_r)
        all_azimuth_bins_t.append(to_store_t)
        all_azimuth_bins_z.append(to_store_z)

    # divide all_azimuth_bins into seprated bins
    for to_plot_trace_item_r, to_plot_trace_item_t, to_plot_trace_item_z in zip(all_azimuth_bins_r, all_azimuth_bins_t, all_azimuth_bins_z):
        info = to_plot_trace_item_r.property
        azimuth = info["azimuth"]
        if(azimuth == 360):
            azimuth = 0
        index_azimuth_bin = int(azimuth//bin_width)
        if(problem_amp(to_plot_trace_item_r) or problem_amp(to_plot_trace_item_t) or problem_amp(to_plot_trace_item_z)):
            continue
        azimuth_bins_r[index_azimuth_bin].append(to_plot_trace_item_r)
        azimuth_bins_t[index_azimuth_bin].append(to_plot_trace_item_t)
        azimuth_bins_z[index_azimuth_bin].append(to_plot_trace_item_z)

    return azimuth_bins_r, azimuth_bins_t, azimuth_bins_z


def get_property_times(stla, stlo, evla, evlo, evdp):
    property_times = {
        "first_p": None,
        "first_s": None,
        "surface_wave": None,
        "local_station": False,
        "gcarc": None,
        "azimuth": None
    }

    # sphere gcircle distance, since taup use sphere
    gcarc = locations2degrees(stla, stlo, evla, evlo)
    property_times["gcarc"] = gcarc

    # calculate first arrivals
    arrivals = model.get_travel_times(source_depth_in_km=evdp,
                                      distance_in_degree=gcarc,
                                      phase_list=["p", "P", "s", "S", "3.5kmps"])

    for item in arrivals:
        # find p
        if(property_times["first_p"] == None):
            if(item.name == "p" or item.name == "P"):
                property_times["first_p"] = item.time

        # find s
        if(property_times["first_s"] == None):
            if(item.name == "s" or item.name == "S"):
                property_times["first_s"] = item.time

        # find surface wave
        if(property_times["surface_wave"] == None):
            if(item.name == "3.5kmps"):
                property_times["surface_wave"] = item.time

    # see if it's local stations:
    for item in arrivals:
        if(item.name == "p" or item.name == "s"):
            property_times["local_station"] = True
            break
        elif(item.name == "P" or item.name == "S"):
            property_times["local_station"] = False
            break

    # get azimuth, from the source to the stations
    _, property_times["azimuth"], _ = gps2dist_azimuth(evla, evlo, stla, stlo)

    # always could success
    return property_times


def generate_ordered_structure_for_plotting(azimuth_bins_r, azimuth_bins_t, azimuth_bins_z, bin_width=15):
    """
    output a list of plotting_order_structure in the order of rising distance (y:index), rising azimuth, z->r->t
    """
    azimuth_bin_number = 360//bin_width
    result = []  # each item in result represents a page

    # for azimuth_bins_z
    for azimuth_range_index in range(azimuth_bin_number):
        to_plot_trace_in_this_range = azimuth_bins_z[azimuth_range_index]
        number_to_plot_trace_in_this_range = len(to_plot_trace_in_this_range)
        # order to_plot_trace_in_this_range
        to_plot_trace_in_this_range = sorted(
            to_plot_trace_in_this_range, key=lambda item: item.property["gcarc"])
        split_to_plot_trace_in_this_range = array_split_same_size(
            to_plot_trace_in_this_range, 20)
        index_start = 0
        for item in split_to_plot_trace_in_this_range:
            offset = 20
            result.append(plotting_order_structure(
                item, ("z", azimuth_range_index, index_start, index_start+offset)))
            index_start += offset

    # for azimuth_bins_r
    for azimuth_range_index in range(azimuth_bin_number):
        to_plot_trace_in_this_range = azimuth_bins_r[azimuth_range_index]
        number_to_plot_trace_in_this_range = len(to_plot_trace_in_this_range)
        # order to_plot_trace_in_this_range
        to_plot_trace_in_this_range = sorted(
            to_plot_trace_in_this_range, key=lambda item: item.property["gcarc"])
        split_to_plot_trace_in_this_range = array_split_same_size(
            to_plot_trace_in_this_range, 20)
        for item in split_to_plot_trace_in_this_range:
            result.append(plotting_order_structure(
                item, ("r", azimuth_range_index, index_start, index_start+offset)))

    # for azimuth_bins_t
    for azimuth_range_index in range(azimuth_bin_number):
        to_plot_trace_in_this_range = azimuth_bins_t[azimuth_range_index]
        number_to_plot_trace_in_this_range = len(to_plot_trace_in_this_range)
        # order to_plot_trace_in_this_range
        to_plot_trace_in_this_range = sorted(
            to_plot_trace_in_this_range, key=lambda item: item.property["gcarc"])
        # split_to_plot_trace_in_this_range = np.array_split(
        #     to_plot_trace_in_this_range, 20)
        split_to_plot_trace_in_this_range = array_split_same_size(
            to_plot_trace_in_this_range, 20)

        for item in split_to_plot_trace_in_this_range:
            result.append(plotting_order_structure(
                item, ("t", azimuth_range_index, index_start, index_start+offset)))

    # arange the order in result as we want the same r,t,z appears.
    result_length = len(result)
    newresult = []
    for i in range(int(result_length//3)):
        newresult.append(result[i])
        newresult.append(result[i+int(result_length//3)])
        newresult.append(result[i+int(result_length//3)*2])

    return newresult


def problem_amp(to_plot_trace_item):
    obs_trace = to_plot_trace_item.obs
    syn_trace = to_plot_trace_item.syn
    obs_max = np.max(np.abs(obs_trace.data))
    syn_max = np.max(np.abs(syn_trace.data))
    if(1/5 <= (obs_max/syn_max) <= 5):
        return False
    else:
        return True


def array_split_same_size(thelist, thesize):
    thelist = np.array(thelist)
    result = []
    number_list = len(thelist)
    N_chunks = number_list//thesize+1
    if(number_list % thesize == 0):
        N_chunks -= 1
    for i in range(N_chunks):
        result.append(thelist[i*thesize:(i+1)*thesize])

    return result


def plot_to_pdf(plotting_order_structure_list, output_pdf):
    pdf = matplotlib.backends.backend_pdf.PdfPages(output_pdf)
    figs = plt.figure()
    for each_page_plotting_order_structure in plotting_order_structure_list:
        to_plot_traces = each_page_plotting_order_structure.to_plot_traces
        label = each_page_plotting_order_structure.label
        start_index = label[2]
        end_index = label[3]
        fig = plt.figure(figsize=(10, 10))
        for index, each_plot_trace in enumerate(to_plot_traces):
            index = index+start_index
            obs_raw = each_plot_trace.obs
            syn_raw = each_plot_trace.syn
            theproperty = each_plot_trace.property

            # normalize for syn and obs
            obs = obs_raw.copy()
            syn = syn_raw.copy()
            # cut 1500 seconds window
            obs.trim(obs.stats.starttime, obs.stats.starttime+1500)
            syn.trim(syn.stats.starttime, syn.stats.starttime+1500)
            theall = obspy.Stream()+obs+syn
            theall.normalize(global_max=True)
            x_obs = np.linspace(0, obs.stats.endtime -
                                obs.stats.starttime, obs.stats.npts)
            x_syn = np.linspace(0, syn.stats.endtime -
                                syn.stats.starttime, syn.stats.npts)
            y_obs = 0.5*obs.data+index
            y_syn = 0.5*syn.data+index
            plt.plot(x_obs, y_obs, color="k")
            plt.plot(x_syn, y_syn, color="r")
            plt.scatter(theproperty["first_p"], index,
                        color="green", s=plt.rcParams['lines.markersize']**2/2)
            plt.scatter(theproperty["first_s"], index,
                        color="blue", s=plt.rcParams['lines.markersize']**2/2)
            plt.scatter(theproperty["surface_wave"], index,
                        color="purple", s=plt.rcParams['lines.markersize']**2/2)
        plt.ylim(start_index-0.5, end_index-0.5)
        plt.title(
            f"{label[0]} component, azimuth ranges from {label[1]*15}° to {(label[1]+1)*15}°")
        plt.xlabel("time after the event time (seconds)")
        plt.ylabel("index number")
        plt.yticks(range(start_index, end_index, 1))
        pdf.savefig(fig)
        plt.close(fig=fig)
    plt.close(fig=figs)
    pdf.close()


def main(obs_path, syn_path, bin_width=15, output_pdf="./figures.pdf"):
    ds_obs = pyasdf.ASDFDataSet(obs_path, mode="r")
    ds_syn = pyasdf.ASDFDataSet(syn_path, mode="r")
    azimuth_bins_r, azimuth_bins_t, azimuth_bins_z = get_to_plot_traces_for_each_azimuth_bin(
        ds_obs, ds_syn, bin_width=bin_width)
    plotting_order_structure_list = generate_ordered_structure_for_plotting(
        azimuth_bins_r, azimuth_bins_t, azimuth_bins_z, bin_width=bin_width)
    # output to pdf
    plot_to_pdf(plotting_order_structure_list, output_pdf)
