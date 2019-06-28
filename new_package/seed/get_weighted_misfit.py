import json
import numpy as np


def add_distance_weight(misfit_dict):
    body_phases = ["p", "s", "pn"]
    surf_phases = ["surf", "surf_rs"]

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
                elif(phase in surf_phases):
                    misfit_values[phase] *= mul_surf
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
    for key in misfit_dict:
        azimuth = misfit_dict[key]['property_times']['azimuth']

        azimuth_begin = azimuth-bin_width
        azimuth_end = azimuth+bin_width
        # azimuth will be in [0,360)
        if(azimuth_begin >= 0 and azimuth_end <= 360):
            azimuth_within_range = azimuth_array[azimuth_array >=
                                                 azimuth_begin][azimuth_array <= azimuth_end]
            count_in_bin = len(azimuth_within_range)
        elif(azimuth_begin < 0 and azimuth_end <= 360):
            azimuth_begin_360 = azimuth_begin+360
            if(azimuth_begin_360 < 0):
                raise Exception("bin width too large")
            if(azimuth_begin_360 <= azimuth_end):
                count_in_bin = len(azimuth_array)
            else:
                count1 = len(
                    azimuth_array[azimuth_array <= azimuth_end][azimuth_array >= 0])
                count2 = len(
                    azimuth_array[azimuth_array >= azimuth_begin_360][azimuth_array <= 360])
                count_in_bin = count1+count2
        elif(azimuth_begin >= 0 and azimuth_end > 360):
            azimuth_end_360 = azimuth_end-360
            if(azimuth_end_360 > 360):
                raise Exception("bin width too large")
            if(azimuth_end_360 >= azimuth_begin):
                count_in_bin = len(azimuth_array)
            else:
                count1 = len(
                    azimuth_array[azimuth_array <= azimuth_end_360][azimuth_array >= 0])
                count2 = len(
                    azimuth_array[azimuth_array >= azimuth_begin][azimuth_array <= 360])
                count_in_bin = count1+count2
        else:
            raise Exception("bin width is not appropriate")

        weight_azimuth = len(azimuth_array)/count_in_bin
        info_this_net_sta = misfit_dict[key]
        for misfit_cha in ['misfit_r', 'misfit_t', 'misfit_z']:
            misfit_values = info_this_net_sta[misfit_cha]
            for phase in misfit_values:
                if(misfit_values[phase] == None):
                    continue
                misfit_values[phase] *= weight_azimuth
