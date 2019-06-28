import json
import numpy as np


def add_distance_weight(misfit_dict):
    body_phases = ["p", "s", "pn"]

    for net_sta in misfit_dict:
        info_this_net_sta = misfit_dict[net_sta]
        gcarc = info_this_net_sta['property_times']['gcarc']

        mul_body = gcarc
        mul_surf = np.sqrt(gcarc)

        for misfit_cha in ['misfit_r', 'misfit_t', 'misfit_z']:
            misfit_values = info_this_net_sta[misfit_cha]
            for phase in misfit_values:
                if(misfit_values[phase] == None):
                    continue
                if(phase in body_phases):
                    misfit_values[phase] *= mul_body
                elif(phase == "surf_rs"):
                    misfit_values[phase] *= mul_surf
                elif(phase == "surf"):
                    # don't mul r here
                    pass
                else:
                    raise Exception("the name of phase is wrong")

    return misfit_dict


def add_azimuth_weight(misfit_dict, bin_width):
    # first we get a numpy array to store all the azimuths
    station_nummber = len(misfit_dict)
    azimuth_array = np.zeros(station_nummber)
    for index, key in enumerate(misfit_dict):
        azimuth_array[index] = misfit_dict[key]['property_times']['azimuth']

    # for each station, get the number within the bin_width
    count_in_bin = None
    weight_azimuth_all = 0
    for key in misfit_dict:
        azimuth = misfit_dict[key]['property_times']['azimuth']

        azimuth_begin = azimuth-bin_width
        azimuth_end = azimuth+bin_width
        # azimuth will be in [0,360)
        if(azimuth_begin >= 0 and azimuth_end <= 360):
            azimuth_within_range = azimuth_array[(
                azimuth_array >= azimuth_begin) & (azimuth_array <= azimuth_end)]
            count_in_bin = len(azimuth_within_range)
        elif(azimuth_begin < 0 and azimuth_end <= 360):
            azimuth_begin_360 = azimuth_begin+360
            if(azimuth_begin_360 < 0):
                raise Exception("bin width is too large")
            if(azimuth_begin_360 <= azimuth_end):
                count_in_bin = len(azimuth_array)
            else:
                count1 = len(
                    azimuth_array[(azimuth_array <= azimuth_end) & (azimuth_array >= 0)])
                count2 = len(
                    azimuth_array[(azimuth_array >= azimuth_begin_360) & (azimuth_array <= 360)])
                count_in_bin = count1+count2
        elif(azimuth_begin >= 0 and azimuth_end > 360):
            azimuth_end_360 = azimuth_end-360
            if(azimuth_end_360 > 360):
                raise Exception("bin width too large")
            if(azimuth_end_360 >= azimuth_begin):
                count_in_bin = len(azimuth_array)
            else:
                count1 = len(
                    azimuth_array[(azimuth_array <= azimuth_end_360) & (azimuth_array >= 0)])
                count2 = len(
                    azimuth_array[(azimuth_array >= azimuth_begin) & (azimuth_array <= 360)])
                count_in_bin = count1+count2
        else:
            raise Exception("bin width is not appropriate")

        weight_azimuth = len(azimuth_array)/count_in_bin
        # weight_azimuth_all += weight_azimuth
        add_in_status = False
        info_this_net_sta = misfit_dict[key]
        for misfit_cha in ['misfit_r', 'misfit_t', 'misfit_z']:
            misfit_values = info_this_net_sta[misfit_cha]
            for phase in misfit_values:
                if(misfit_values[phase] == None):
                    continue
                else:
                    misfit_values[phase] *= weight_azimuth
                    add_in_status = True
        if(add_in_status):
            weight_azimuth_all += weight_azimuth

    # we have to normalize weight_azimuth
    for key in misfit_dict:
        info_this_net_sta = misfit_dict[key]
        for misfit_cha in ['misfit_r', 'misfit_t', 'misfit_z']:
            misfit_values = info_this_net_sta[misfit_cha]
            for phase in misfit_values:
                if(misfit_values[phase] == None):
                    continue
                else:
                    misfit_values[phase] /= weight_azimuth_all

    return misfit_dict


def get_weighted_misfit(misfit_dict, pw, shw, svw, surfw):
    """
    use median of all amp in one phase category to normalize the amplitude,
    divide time window to ignore the influence of the time window length.
    Here the misfit can have added distance and azimuth weight.
    """
    # get median of each category
    # we have four categories: p(pn.z+p.z+p.r+pn.r) sh(s.t) sv(s.r+s.z) surf(rayleigh actually, surf.z+surf.r)
    # for 7 types of phases, get median
    pn_z, pn_r, p_z, p_r, s_z, s_r, s_t, surf_z, surf_r = [
        [] for i in range(9)]

    # append values
    for net_sta in misfit_dict:
        amplitude = misfit_dict[net_sta]["amplitude"]
        pn_z.append(amplitude["z"]["pn"])
        pn_r.append(amplitude["r"]["pn"])
        p_z.append(amplitude["z"]["p"])
        p_r.append(amplitude["r"]["p"])
        s_z.append(amplitude["z"]["s"])
        s_r.append(amplitude["r"]["s"])
        s_t.append(amplitude["t"]["s"])
        surf_z.append(amplitude["z"]["surf"])
        surf_r.append(amplitude["r"]["surf"])

    # drop None and combine pn and p
    p_z = p_z+pn_z
    p_r = p_r+pn_r

    p_z = np.array(p_z)
    p_r = np.array(p_r)
    s_z = np.array(s_z)
    s_r = np.array(s_r)
    s_t = np.array(s_t)
    surf_z = np.array(surf_z)
    surf_r = np.array(surf_r)

    p_z = p_z[p_z != np.array(None)]
    p_r = p_r[p_r != np.array(None)]
    s_z = s_z[s_z != np.array(None)]
    s_r = s_r[s_r != np.array(None)]
    s_t = s_t[s_t != np.array(None)]
    surf_z = surf_z[surf_z != np.array(None)]
    surf_r = surf_r[surf_r != np.array(None)]

    p_z_median = np.median(p_z)
    p_r_median = np.median(p_r)
    s_z_median = np.median(s_z)
    s_r_median = np.median(s_r)
    s_t_median = np.median(s_t)
    surf_z_median = np.median(surf_z)
    surf_r_median = np.median(surf_r)

    #  normalize using window length and median value
    for net_sta in misfit_dict:
        for misfit_type in ["misfit_r", "misfit_t", "misfit_z"]:
            misfit_values = misfit_dict[net_sta][misfit_type]
            for phase in misfit_values:
                window_length = None
                if(misfit_values[phase] == None):
                    continue
                else:
                    cha = misfit_type[-1]
                    if(phase != "surf_rs"):
                        phase_window = phase
                    else:
                        phase_window = "surf"
                    window_length = misfit_dict[net_sta]['window_length'][cha][phase_window]
                    if(phase != "surf"):
                        misfit_values[phase] /= window_length
                    else:
                        pass  # don't update surf result

                    # for median
                    if(cha == "z" and (phase == "p" or phase == "pn")):
                        misfit_values[phase] /= p_z_median
                    elif(cha == "r" and (phase == "p" or phase == "pn")):
                        misfit_values[phase] /= p_r_median
                    elif(cha == "z" and (phase == "s")):
                        misfit_values[phase] /= s_z_median
                    elif(cha == "r" and (phase == "s")):
                        misfit_values[phase] /= s_r_median
                    elif(cha == "t" and (phase == "s")):
                        misfit_values[phase] /= s_t_median
                    elif(cha == "z" and (phase == "surf_rs")):  # don't update surf result
                        misfit_values[phase] /= surf_z_median
                    elif(cha == "r" and (phase == "surf_rs")):
                        misfit_values[phase] /= surf_r_median
                    else:
                        pass

    # add misfit in different stations together
    p_z_all = 0
    p_r_all = 0
    s_z_all = 0
    s_r_all = 0
    s_t_all = 0
    surfrs_z_all = 0
    surfrs_r_all = 0
    surf_z_all = 0
    surf_r_all = 0

    len_p_z = len(p_z)
    len_p_r = len(p_r)
    len_s_z = len(s_z)
    len_s_r = len(s_r)
    len_s_t = len(s_t)
    len_surf_z = len(surf_z)
    len_surf_r = len(surf_r)

    for net_sta in misfit_dict:
        for misfit_type in ["misfit_r", "misfit_t", "misfit_z"]:
            cha = misfit_type[-1]
            for phase in misfit_dict[net_sta][misfit_type]:
                # handle None
                if(misfit_dict[net_sta][misfit_type][phase] == None):
                    continue

                if(cha == "z" and (phase == "p" or phase == "pn")):
                    p_z_all += misfit_dict[net_sta][misfit_type][phase]/len_p_z
                elif(cha == "r" and (phase == "p" or phase == "pn")):
                    p_r_all += misfit_dict[net_sta][misfit_type][phase]/len_p_r
                elif(cha == "z" and (phase == "s")):
                    s_z_all += misfit_dict[net_sta][misfit_type][phase]/len_s_z
                elif(cha == "r" and (phase == "s")):
                    s_r_all += misfit_dict[net_sta][misfit_type][phase]/len_s_r
                elif(cha == "t" and (phase == "s")):
                    s_t_all += misfit_dict[net_sta][misfit_type][phase]/len_s_t
                elif(cha == "z" and (phase == "surf_rs")):
                    surfrs_z_all += misfit_dict[net_sta][misfit_type][phase]/len_surf_z
                elif(cha == "r" and (phase == "surf_rs")):
                    surfrs_r_all += misfit_dict[net_sta][misfit_type][phase]/len_surf_r
                elif(cha == "z" and (phase == "surf")):
                    surf_z_all += misfit_dict[net_sta][misfit_type][phase]/len_surf_z
                elif(cha == "r" and (phase == "surf")):
                    surf_r_all += misfit_dict[net_sta][misfit_type][phase]/len_surf_r
                else:
                    pass

    # use weight to combine phase groups to one value
    result = {}
    result["P"] = 0.5*(p_z_all+p_r_all)
    result["SV"] = 0.5*(s_z_all+s_r_all)
    result["SH"] = s_t_all
    result["surf"] = 0.5*(surfrs_r_all+surfrs_z_all)
    result["surf_mt"] = 0.5*(surf_r_all+surf_z_all)
    result["overall"] = (pw*result["P"]+svw*result["SV"] +
                         shw*result["SH"]+surfw*result["surf"])/(pw+svw+shw+surfw)
    result["p_z"] = p_z_all
    result["p_r"] = p_r_all
    result["s_z"] = s_z_all
    result["s_r"] = s_r_all
    result["s_t"] = s_t_all
    result["surfrs_r"] = surfrs_r_all
    result["surfrs_z"] = surfrs_z_all
    result["surf_r"] = surf_r_all
    result["surf_z"] = surf_z_all

    return result


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


def main(body_json, surf_json, weights, output_json):

    # In[96]: def wrapper(depth, bw):
    #     ...:     f = open(f"./surf_{depth}.json")
    #     ...:     g = open(f"./body_{depth}.json")
    #     ...:     surf = json.load(f)
    #     ...:     body = json.load(g)
    #     ...:     theall = combine_json_dict(body, surf)
    #     ...:     theall = add_distance_weight(theall)
    #     ...:     theall = add_azimuth_weight(theall, bw)
    #     ...: return get_weighted_misfit(theall, 1, 1, 1, 1)
