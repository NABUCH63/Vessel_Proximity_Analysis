# import libraries
import pandas as pd
import datetime
from geopy.distance import geodesic as gp
import os
from geographiclib.geodesic import Geodesic as gd

# set directory for AIS data
dir_list = os.listdir("../SF_AIS")

# load grid into pandas dataframe
grid_file = pd.read_csv("../GRIDS/SF_500m_RES.csv")

# establish new columns for the measurements and ROTR
grid_file["Total_Interactions"] = 0
grid_file["crossing"] = 0
grid_file["overtaking"] = 0
grid_file["headon"] = 0
grid_file["Passenger_Interactions"] = 0
grid_file["pass_flagged"] = 0
grid_file["pass_crossing"] = 0
grid_file["pass_overtaking"] = 0
grid_file["pass_headon"] = 0
grid_file["CT_Interactions"] = 0
grid_file["CT_flagged"] = 0
grid_file["CT_crossing"] = 0
grid_file["CT_overtaking"] = 0
grid_file["CT_headon"] = 0
grid_file["Flagged_Interactions"] = 0
grid_file["flagged_crossing"] = 0
grid_file["flagged_overtaking"] = 0
grid_file["flagged_headon"] = 0

grid_file["Nonrec_Interactions"] = 0
grid_file["Flagged_Nonrec_Interactions"] = 0
grid_file["nonrec_crossing"] = 0
grid_file["nonrec_overtaking"] = 0
grid_file["nonrec_headon"] = 0

min_dist = .15
flag_dist = .05

# loop through files in the AIS directory
for file in dir_list:

    # select which files in directory
    if "AIS_2021_07" in file or "AIS_2021_08" in file or "AIS_2021_09" in file:
        # load AIS csv into pandas dataframe
        AIS_data_raw = pd.read_csv(f"../SF_AIS/{file}", encoding="UTF-8")
        AIS_data_raw["BaseDateTime"] = pd.to_datetime(AIS_data_raw["BaseDateTime"], format="%H:%M:%S")
        print(AIS_data_raw["BaseDateTime"].dtype)
        # initiate timer for process time
        timer_start = datetime.datetime.now()
        # loop through grid points
        for row in grid_file.index:

            # set default values for counters and for a starting minimum distance
            halfmi = 0
            halfmi_x = 0
            halfmi_over = 0
            halfmi_head = 0
            halfmi_pass = 0
            halfmi_pass_flag = 0
            halfmi_x_pass = 0
            halfmi_over_pass = 0
            halfmi_head_pass = 0
            halfmi_CT = 0
            halfmi_CT_flag = 0
            halfmi_x_CT = 0
            halfmi_over_CT = 0
            halfmi_head_CT = 0
            halfmi_flag = 0
            halfmi_x_flag = 0
            halfmi_over_flag = 0
            halfmi_head_flag = 0
            halfmi_nonrec = 0
            halfmi_nonrec_flag = 0
            halfmi_x_nonrec = 0
            halfmi_over_nonrec = 0
            halfmi_head_nonrec = 0

            # define search area surrounding grid point ~500 meters (567yd/2000yd * .01666 deg per nm)
            lat_c = grid_file["LAT"][row]
            lon_c = grid_file["LON"][row]
            lat_tl = lat_c + .00456
            lat_br = lat_c - .00456
            lon_tl = lon_c - .00456
            lon_br = lon_c + .00456

            # load AIS data for the search area
            AIS_data = AIS_data_raw[AIS_data_raw["LAT"] > lat_br]
            AIS_data = AIS_data[AIS_data["LAT"] < lat_tl]
            AIS_data = AIS_data[AIS_data["LON"] > lon_tl]
            AIS_data = AIS_data[AIS_data["LON"] < lon_br]

            # sort by datetime and reset index
            AIS_data = AIS_data.sort_values(["BaseDateTime"], ascending=[True]).reset_index(drop=True).reset_index()
            AIS_data.set_index("index", inplace=True)

            temp_df = AIS_data.copy()

            # create empty MMSI index to capture observed vessel pairs
            MMSI_index = set()

            # set a minute index of all unique timestamps loaded for grid point
            min_index = AIS_data["BaseDateTime"].unique()

            # set a minimum minute reference
            min_ref = "0:00:00"

            # if the timestamp is greater than an hour from the reference, empty the observation index and capture time
            for minute in min_index:
                if abs((minute - pd.to_datetime(min_ref)).total_seconds()) / 60 > 20:
                    MMSI_index = set()
                    min_ref = minute

                    minlo = minute-pd.Timedelta(seconds=1)
                    minhi = minute+pd.Timedelta(seconds=1)

                # while looping through the min_index, grab only those values that are the same time
                temp_df = AIS_data[(AIS_data["BaseDateTime"] == minlo) | (AIS_data["BaseDateTime"] == minhi) | (AIS_data["BaseDateTime"] == minute)].reset_index(drop=True)

                # loop through the vessels captured and compare to every other vessel
                if len(temp_df) > 0:

                    for vessel1 in range(len(temp_df)):
                        for vessel2 in range(vessel1, len(temp_df)):
                            # the vessels cannot be compared to themselves
                            if temp_df["MMSI"][vessel1] and temp_df["MMSI"][vessel2] and temp_df["MMSI"][vessel1] != temp_df["MMSI"][vessel2] and temp_df["SOG"][vessel1] > 5 and temp_df["SOG"][vessel2] > 5:
                                # check if vessels are not in the MMSI_index
                                if tuple(sorted([temp_df["MMSI"][vessel1], temp_df["MMSI"][vessel2]])) not in MMSI_index:

                                    # if not in the index, add the pair
                                    MMSI_index.add(tuple(sorted([temp_df["MMSI"][vessel1], temp_df["MMSI"][vessel2]])))

                                    # calc distance between vessels for CPA
                                    dist = gp((temp_df["LAT"][vessel1], temp_df["LON"][vessel1]), (temp_df["LAT"][vessel2], temp_df["LON"][vessel2])).nm

                                    # add interaction to the total counter and vessel type counters
                                    halfmi += 1
                                    if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                        halfmi_pass += 1
                                    if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                        halfmi_CT += 1
                                    if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                        halfmi_nonrec += 1
                                    # if distance is less than half a nautical mile, add to counter

                                    if dist <= flag_dist:
                                        halfmi_flag += 1
                                        if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                            halfmi_pass_flag += 1
                                        if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                            halfmi_CT_flag += 1
                                        if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                            halfmi_nonrec_flag += 1

                                    # dont allow negative headings from bad input data
                                    if temp_df["COG"][vessel1] >= 0 and temp_df["COG"][vessel2] >= 0:

                                        # calc the relative larger and smaller headings of the vessels being compared, then the net delta (difference) in heading between them.
                                        if temp_df["COG"][vessel1] > temp_df["COG"][vessel2]:
                                            larger_head = temp_df["COG"][vessel1]
                                            smaller_head = temp_df["COG"][vessel2]
                                        else:
                                            larger_head = temp_df["COG"][vessel2]
                                            smaller_head = temp_df["COG"][vessel1]

                                        if larger_head - smaller_head > 180:
                                            delta = 360 - (larger_head - smaller_head)
                                        else:
                                            delta = larger_head - smaller_head


                                        if delta <= 45: #overtaking

                                            # average heading
                                            A = temp_df["COG"][vessel1]
                                            B = temp_df["COG"][vessel2]
                                            AVG_heading = (A + B)/2

                                            # if AVG_heading is in one of 8 sectors, then determine what criteria of lat/lon differences are needed for the tailing vessel
                                                ### if North
                                            if AVG_heading >= 337.7 and AVG_heading < 22.5:
                                                if temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] > 0:
                                                    if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1

                                                elif temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] > 0:
                                                    if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][
                                                                vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                ### if North East
                                            elif AVG_heading >= 22.5 and AVG_heading < 67.5:
                                                if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] > 0) and (temp_df["LON"][vessel1] - temp_df["LON"][vessel2] > 0):
                                                    if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][
                                                                vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] > 0) and (temp_df["LON"][vessel2] - temp_df["LON"][vessel1] > 0):
                                                    if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][
                                                                vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][
                                                                vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                ### if East
                                            elif AVG_heading >= 67.5 and AVG_heading < 112.5:
                                                if temp_df["LON"][vessel1] - temp_df["LON"][vessel2] > 0:
                                                    if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                elif temp_df["LON"][vessel2] - temp_df["LON"][vessel1] > 0:
                                                    if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                ### if South East
                                            elif AVG_heading >= 112.5 and AVG_heading < 157.5:
                                                if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] < 0) and (temp_df["LON"][vessel1] - temp_df["LON"][vessel2] > 0):
                                                    if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] < 0) and (temp_df["LON"][vessel2] - temp_df["LON"][vessel1] > 0):
                                                    if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                ### if South
                                            elif AVG_heading >= 157.5 and AVG_heading < 202.5:
                                                if temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] < 0:
                                                    if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                elif temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] < 0:
                                                    if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                ### if South West
                                            elif AVG_heading >= 202.5 and AVG_heading < 247.5:
                                                if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] < 0) and (temp_df["LON"][vessel1] - temp_df["LON"][vessel2] < 0):
                                                    if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] < 0) and (temp_df["LON"][vessel2] - temp_df["LON"][vessel1] < 0):
                                                    if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                ### if West
                                            elif AVG_heading >= 247.5 and AVG_heading < 292.5:
                                                if temp_df["LON"][vessel1] - temp_df["LON"][vessel2] < 0:
                                                    if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                elif temp_df["LON"][vessel2] - temp_df["LON"][vessel1] < 0:
                                                    if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                ### if North West
                                            elif AVG_heading >= 292.5 and AVG_heading < 337.5:
                                                if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] > 0) and (temp_df["LON"][vessel1] - temp_df["LON"][vessel2] < 0):
                                                    if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1
                                                elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] > 0) and (temp_df["LON"][vessel2] - temp_df["LON"][vessel1] < 0):
                                                    if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 2:
                                                        halfmi_over += 1
                                                        if dist < min_dist:
                                                            if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                                halfmi_over_pass += 1
                                                            if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                                halfmi_over_CT += 1
                                                            if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                                halfmi_over_nonrec += 1
                                                        if dist <= flag_dist:
                                                            halfmi_over_flag += 1


                                        if delta > 45 and delta < 135: # crossing

                                            v1_2 = gd.WGS84.Inverse(temp_df["LAT"][vessel1], temp_df["LON"][vessel1], temp_df["LAT"][vessel2], temp_df["LON"][vessel2])['azi1']
                                            v2_1 = gd.WGS84.Inverse(temp_df["LAT"][vessel2], temp_df["LON"][vessel2], temp_df["LAT"][vessel1], temp_df["LON"][vessel1])['azi1']

                                            if v1_2 < 0:
                                                v1_2_conv = v1_2 + 360
                                            else:
                                                v1_2_conv = v1_2

                                            if v2_1 < 0:
                                                v2_1_conv = v2_1 + 360
                                            else:
                                                v2_1_conv = v2_1

                                            if v1_2_conv > temp_df["COG"][vessel1]:
                                                larger_head1 = v1_2_conv
                                                smaller_head1 = temp_df["COG"][vessel1]
                                            else:
                                                larger_head1 = temp_df["COG"][vessel1]
                                                smaller_head1 = v1_2_conv

                                            if v2_1_conv > temp_df["COG"][vessel2]:
                                                larger_head2 = v2_1_conv
                                                smaller_head2 = temp_df["COG"][vessel2]
                                            else:
                                                larger_head2 = temp_df["COG"][vessel2]
                                                smaller_head2 = v2_1_conv

                                            if larger_head1 - smaller_head1 > 180:
                                                delta1 = 360 - (larger_head1 - smaller_head1)
                                            else:
                                                delta1 = larger_head1 - smaller_head1

                                            if larger_head2 - smaller_head2 > 180:
                                                delta2 = 360 - (larger_head2 - smaller_head2)
                                            else:
                                                delta2 = larger_head2 - smaller_head2

                                            if delta1 < 90 and delta2 < 90:
                                                halfmi_x += 1
                                                if dist < min_dist:
                                                    if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                        halfmi_x_pass += 1
                                                    if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                        halfmi_x_CT += 1
                                                    if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                        halfmi_x_nonrec += 1
                                                if dist <= flag_dist:
                                                    halfmi_x_flag += 1

                                        if delta >= 135: # head on
                                            halfmi_head += 1
                                            if dist < min_dist:
                                                if (temp_df["VesselType"][vessel1] >= 60 and temp_df["VesselType"][vessel1] <= 69) or (temp_df["VesselType"][vessel2] >= 60 and temp_df["VesselType"][vessel2] <= 69):
                                                    halfmi_head_pass += 1
                                                if ((temp_df["VesselType"][vessel1] >= 70 and temp_df["VesselType"][vessel1] <= 89) or (temp_df["VesselType"][vessel2] >= 70 and temp_df["VesselType"][vessel2] <= 89)) and temp_df["VesselType"][vessel1] not in [31, 32, 52] and temp_df["VesselType"][vessel2] not in [31, 32, 52]:
                                                    halfmi_head_CT += 1
                                                if temp_df["VesselType"][vessel1] not in [0, 36, 37, 31, 32, 52] and temp_df["VesselType"][vessel2] not in [0, 36, 37, 31, 32, 52]:
                                                    halfmi_head_nonrec += 1
                                            if dist <= flag_dist:
                                                halfmi_head_flag += 1

            # process check read-out
            if row % 2500 == 0:
                print(row)


            grid_file.loc[row, "Total_Interactions"] = halfmi
            grid_file.loc[row, "crossing"] = halfmi_x
            grid_file.loc[row, "overtaking"] = halfmi_over
            grid_file.loc[row, "headon"] = halfmi_head
            grid_file.loc[row, "CT_Interactions"] = halfmi_CT
            grid_file.loc[row, "CT_crossing"] = halfmi_x_CT
            grid_file.loc[row, "CT_overtaking"] = halfmi_over_CT
            grid_file.loc[row, "CT_headon"] = halfmi_head_CT
            grid_file.loc[row, "CT_flagged"] = halfmi_CT_flag
            grid_file.loc[row, "Passenger_Interactions"] = halfmi_pass
            grid_file.loc[row, "pass_crossing"] = halfmi_x_pass
            grid_file.loc[row, "pass_overtaking"] = halfmi_over_pass
            grid_file.loc[row, "pass_headon"] = halfmi_head_pass
            grid_file.loc[row, "pass_flagged"] = halfmi_pass_flag
            grid_file.loc[row, "Flagged_Interactions"] = halfmi_flag
            grid_file.loc[row, "flagged_crossing"] = halfmi_x_flag
            grid_file.loc[row, "flagged_overtaking"] = halfmi_over_flag
            grid_file.loc[row, "flagged_headon"] = halfmi_head_flag

            grid_file.loc[row, "Nonrec_Interactions"] = halfmi_nonrec
            grid_file.loc[row, "Flagged_Nonrec_Interactions"] = halfmi_nonrec_flag
            grid_file.loc[row, "nonrec_crossing"] = halfmi_x_nonrec
            grid_file.loc[row, "nonrec_overtaking"] = halfmi_over_nonrec
            grid_file.loc[row, "nonrec_headon"] = halfmi_head_nonrec


        file_split = file.split(".")

        grid_file.to_csv(f"../Result/Vessel_Interaction_{file_split[0]}.csv", index=False)
        print(file_split[0])
        print(f"{abs((timer_start - datetime.datetime.now()).total_seconds()) / 60} minutes")