from recordtype import recordtype
import numpy as np
import json

misfit_windows = recordtype("misfit_windows", [
                            "channel", "phase", "misfit", "length", "amplitude", "gcarc", "azimuth", "azimuth_weight"])


def extract_information(json_dict):
    p_z = []
    p_r = []
    s_z = []
    s_r = []
    s_t = []
    surf_z = []
    surf_r = []
    surf_z_mt = []
    surf_r_mt = []
    for net_sta in json_dict:
        info = json_dict[net_sta]

        if((info["misfit_r"]["pn"] != None) and (info["amplitude"]["r"]["pn"] != None)):
            p_r.append(misfit_windows(
                "r", "pn", info["misfit_r"]["pn"], info["window_length"]["r"]["pn"], info["amplitude"]["r"]["pn"], info["property_times"]["gcarc"], info["property_times"]["azimuth"], 0))
        if((info["misfit_z"]["pn"] != None) and (info["amplitude"]["z"]["pn"] != None)):
            p_z.append(misfit_windows(
                "z", "pn", info["misfit_z"]["pn"], info["window_length"]["z"]["pn"], info["amplitude"]["z"]["pn"], info["property_times"]["gcarc"], info["property_times"]["azimuth"], 0))
        if((info["misfit_r"]["p"] != None) and (info["amplitude"]["r"]["p"] != None)):
            p_r.append(misfit_windows(
                "r", "p", info["misfit_r"]["p"], info["window_length"]["r"]["p"], info["amplitude"]["r"]["p"], info["property_times"]["gcarc"], info["property_times"]["azimuth"], 0))
        if((info["misfit_z"]["p"] != None) and (info["amplitude"]["z"]["p"] != None)):
            p_z.append(misfit_windows(
                "z", "p", info["misfit_z"]["p"], info["window_length"]["z"]["p"], info["amplitude"]["z"]["p"], info["property_times"]["gcarc"], info["property_times"]["azimuth"], 0))
        if((info["misfit_r"]["s"] != None) and (info["amplitude"]["r"]["s"] != None)):
            s_r.append(misfit_windows(
                "r", "s", info["misfit_r"]["s"], info["window_length"]["r"]["s"], info["amplitude"]["r"]["s"], info["property_times"]["gcarc"], info["property_times"]["azimuth"], 0))
        if((info["misfit_t"]["s"] != None) and (info["amplitude"]["t"]["s"] != None)):
            s_t.append(misfit_windows(
                "t", "s", info["misfit_t"]["s"], info["window_length"]["t"]["s"], info["amplitude"]["t"]["s"], info["property_times"]["gcarc"], info["property_times"]["azimuth"], 0))
        if((info["misfit_z"]["s"] != None) and (info["amplitude"]["z"]["s"] != None)):
            s_z.append(misfit_windows(
                "z", "s", info["misfit_z"]["s"], info["window_length"]["z"]["s"], info["amplitude"]["z"]["s"], info["property_times"]["gcarc"], info["property_times"]["azimuth"], 0))
        if((info["misfit_r"]["surf_rs"] != None) and (info["amplitude"]["r"]["surf"] != None)):
            surf_r.append(misfit_windows(
                "r", "surf", info["misfit_r"]["surf_rs"], info["window_length"]["r"]["surf"], info["amplitude"]["r"]["surf"], info["property_times"]["gcarc"], info["property_times"]["azimuth"], 0))
        if((info["misfit_z"]["surf_rs"] != None) and (info["amplitude"]["z"]["surf"] != None)):
            surf_z.append(misfit_windows(
                "z", "surf", info["misfit_z"]["surf_rs"], info["window_length"]["z"]["surf"], info["amplitude"]["z"]["surf"], info["property_times"]["gcarc"], info["property_times"]["azimuth"], 0))
        if((info["misfit_r"]["surf"] != None) and (info["amplitude"]["r"]["surf"] != None)):
            surf_r_mt.append(misfit_windows(
                "r", "surf_mt", info["misfit_r"]["surf"], info["window_length"]["r"]["surf"], info["amplitude"]["r"]["surf"], info["property_times"]["gcarc"], info["property_times"]["azimuth"], 0))
        if((info["misfit_z"]["surf"] != None) and (info["amplitude"]["z"]["surf"] != None)):
            surf_z_mt.append(misfit_windows(
                "z", "surf_mt", info["misfit_z"]["surf"], info["window_length"]["z"]["surf"], info["amplitude"]["z"]["surf"], info["property_times"]["gcarc"], info["property_times"]["azimuth"], 0))

    return p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt


def adjust_distance_influence(p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt):
    """
    the distance coefficient shouldn't be considered as a type of weight, but a kind of "normalization"
    """
    for item in p_z:
        item.misfit = item.misfit*item.gcarc
        item.amplitude = item.amplitude*item.gcarc
    for item in p_r:
        item.misfit = item.misfit*item.gcarc
        item.amplitude = item.amplitude*item.gcarc
    for item in s_z:
        item.misfit = item.misfit*item.gcarc
        item.amplitude = item.amplitude*item.gcarc
    for item in s_r:
        item.misfit = item.misfit*item.gcarc
        item.amplitude = item.amplitude*item.gcarc
    for item in s_t:
        item.misfit = item.misfit*item.gcarc
        item.amplitude = item.amplitude*item.gcarc
    for item in surf_z:
        item.misfit = item.misfit*np.sqrt(item.gcarc)
        item.amplitude = item.amplitude*np.sqrt(item.gcarc)
    for item in surf_r:
        item.misfit = item.misfit*np.sqrt(item.gcarc)
        item.amplitude = item.amplitude*np.sqrt(item.gcarc)
    return p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt


def adjust_timewindow_influence(p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt):
    """
    we should use the misfit per second
    """
    for item in p_z:
        item.misfit = item.misfit/item.length
    for item in p_r:
        item.misfit = item.misfit/item.length
    for item in s_z:
        item.misfit = item.misfit/item.length
    for item in s_r:
        item.misfit = item.misfit/item.length
    for item in s_t:
        item.misfit = item.misfit/item.length
    for item in surf_z:
        item.misfit = item.misfit/item.length
    for item in surf_r:
        item.misfit = item.misfit/item.length
    return p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt


def calculate_azimuth_weight(p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt, bin_angle=20):
    """
    only calculate azimuth weight, consider number of windows within the bin angle for the same kind of phase
    """
    # get numpy arrays storing azimuth information for each type of windows
    def get_azimuth_weight_for_a_type(misfit_win_list):
        N_misfit_win = len(misfit_win_list)
        azimuth_array = np.zeros(N_misfit_win)
        # store to azimuth_array
        for index, misfit_win in enumerate(misfit_win_list):
            azimuth_array[index] = misfit_win.azimuth
        return azimuth_array

    # get the number of stations inside the azimuth bin, don't consider extreme conditions
    def get_number_of_stations_within_bin(azimuth_array, bin_angle, azimuth_this_station):
        azimuth_start = azimuth_this_station-bin_angle/2
        azimuth_end = azimuth_this_station+bin_angle/2
        # different conditions
        selected_azimuth_list = None
        if((azimuth_start >= 0) and (azimuth_end <= 360)):
            selected_azimuth_list = azimuth_array[(
                azimuth_array >= azimuth_start) & (azimuth_array <= azimuth_end)]
        elif((azimuth_start < 0) and (azimuth_end <= 360)):
            azimuth_start = azimuth_start+360
            selected_azimuth_list = azimuth_array[(
                azimuth_array >= azimuth_start) | (azimuth_array <= azimuth_end)]
        elif((azimuth_start >= 0) and (azimuth_end > 360)):
            azimuth_end = azimuth_end-360
            selected_azimuth_list = azimuth_array[(
                azimuth_array >= azimuth_start) | (azimuth_array <= azimuth_end)]
        else:
            raise Exception(
                "not implemented, azimuth_this_station is too large")
        return len(selected_azimuth_list)

    # get azimuth_weight for each window
    all_list = [p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt]
    for pha_cha_item in all_list:
        weight_store = np.zeros(len(pha_cha_item))
        azimuth_array = get_azimuth_weight_for_a_type(pha_cha_item)
        for index, window_item in enumerate(pha_cha_item):
            azimuth_this_station = window_item.azimuth
            N_in = get_number_of_stations_within_bin(
                azimuth_array, bin_angle, azimuth_this_station)
            # wait to normalize
            weight_store[index] = 1/N_in

            # ! restrict azimuth range
            if(15 < azimuth_this_station < 225):
                weight_store[index] = 0

        weight_all = np.sum(weight_store)
        weight_store = weight_store/weight_all

        # now we can set the azimuth_weight
        for index, window_item in enumerate(pha_cha_item):
            pha_cha_item[index].azimuth_weight = weight_store[index]
    return p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt


def get_weighted_misfit(p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt):
    """
    Here we only consider the azimuth weight as the distance has the meaning of "normalization"
    """
    all_list = [p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt]
    all_misfit_list = [0.0 for item in range(len(all_list))]
    for index, pha_cha_item in enumerate(all_list):
        weighted_misfit = 0.0
        for item in pha_cha_item:
            weighted_misfit += item.misfit*item.azimuth_weight
        all_misfit_list[index] = weighted_misfit
    return np.array(all_misfit_list)


def combine_json_dict(body_dict, surf_dict):
    """
    combine the json dict for both the surface wave and the body wave
    """
    for net_sta in body_dict:
        for level1_key in ["misfit_r", "misfit_t", "misfit_z", "property_times"]:
            for level2_key in body_dict[net_sta][level1_key]:
                body_dict[net_sta][level1_key][level2_key] = body_dict[net_sta][
                    level1_key][level2_key] or surf_dict[net_sta][level1_key][level2_key]

        for level1_key in ["window_length", "amplitude"]:
            for level2_key in body_dict[net_sta][level1_key]:
                for level3_key in body_dict[net_sta][level1_key][level2_key]:
                    body_dict[net_sta][level1_key][level2_key][level3_key] = body_dict[net_sta][level1_key][
                        level2_key][level3_key] or surf_dict[net_sta][level1_key][level2_key][level3_key]
    return body_dict


def main(body_json, surf_json, bin_angle):
    # combine json files
    body_f = open(body_json, "r")
    surf_f = open(surf_json, "r")
    body_dict = json.load(body_f)
    surf_dict = json.load(surf_f)
    json_dict = combine_json_dict(body_dict, surf_dict)

    # extract to windows
    p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt = extract_information(
        json_dict)
    p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt = adjust_distance_influence(
        p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt)
    p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt = adjust_timewindow_influence(
        p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt)
    p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt = calculate_azimuth_weight(
        p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt, bin_angle=bin_angle)
    p_z_misfit, p_r_misfit, s_z_misfit, s_r_misfit, s_t_misfit, surf_z_misfit, surf_r_misfit, surf_z_mt_misfit, surf_r_mt_misfit = get_weighted_misfit(
        p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt)

    # print them out, only for debug
    print("p_z_misfit", p_z_misfit)
    print("p_r_misfit", p_r_misfit)
    print("s_z_misfit", s_z_misfit)
    print("s_r_misfit", s_r_misfit)
    print("s_t_misfit", s_t_misfit)
    print("surf_z_misfit", surf_z_misfit)
    print("surf_r_misfit", surf_r_misfit)
    print("surf_z_mt_misfit", surf_z_mt_misfit)
    print("surf_r_mt_misfit", surf_r_mt_misfit)

    # get the weighted misfit
    return p_z_misfit, p_r_misfit, s_z_misfit, s_r_misfit, s_t_misfit, surf_z_misfit, surf_r_misfit, surf_z_mt_misfit, surf_r_mt_misfit


def easy_main(bin_angle):
    """
    for plotting purpose
    """
    thelist = ["-16.0", "-12.0", "-8.0", "-4.0",
               "0.0", "4.0", "8.0", "12.0", "16.0"]
    p_z, p_r, s_z, s_r, s_t, surf_z, surf_r, surf_z_mt, surf_r_mt = [
        [] for i in range(9)]
    p_all = []
    sv_all = []
    sh_all = []
    ray_all = []
    theall = []
    theall_nosurf = []
    for depth in thelist:
        surf_json = f"surf_d{depth}.json"
        body_json = f"body_d{depth}.json"
        p_z_misfit, p_r_misfit, s_z_misfit, s_r_misfit, s_t_misfit, surf_z_misfit, surf_r_misfit, surf_z_mt_misfit, surf_r_mt_misfit = main(
            body_json, surf_json, bin_angle)
        p_z.append(p_z_misfit)
        p_r.append(p_r_misfit)
        s_z.append(s_z_misfit)
        s_r.append(s_r_misfit)
        s_t.append(s_t_misfit)
        surf_z.append(surf_z_misfit)
        surf_r.append(surf_r_misfit)
        surf_z_mt.append(surf_z_mt_misfit)
        surf_r_mt.append(surf_r_mt_misfit)

        p_all.append(0.5*(p_z_misfit+p_r_misfit))
        sv_all.append(0.5*(s_z_misfit+s_r_misfit))
        sh_all.append(s_t_misfit)
        ray_all.append(0.5*(surf_z_misfit+surf_r_misfit))
        theall.append(0.25*(0.5*(p_z_misfit+p_r_misfit) +
                            0.5*(s_z_misfit+s_r_misfit)+s_t_misfit+0.5*(surf_z_misfit+surf_r_misfit)))
        theall_nosurf.append(1/3*(0.5*(p_z_misfit+p_r_misfit) +
                                  0.5*(s_z_misfit+s_r_misfit)+s_t_misfit))
    print("p_z_misfit", p_z)
    print("p_r_misfit", p_r)
    print("s_z_misfit", s_z)
    print("s_r_misfit", s_r)
    print("s_t_misfit", s_t)
    print("surf_z_misfit", surf_z)
    print("surf_r_misfit", surf_r)
    print("surf_z_mt_misfit", surf_z)
    print("surf_r_mt_misfit", surf_r)
    print("p_all", p_all)
    print("sv_all", sv_all)
    print("sh_all", sh_all)
    print("ray_all", ray_all)
    print("theall", theall)
    print("theall_nosurf", theall_nosurf)
