# import libraries
import pandas as pd
import datetime
from geopy.distance import geodesic as gp
import os
from geographiclib.geodesic import Geodesic as gd

# set directory for AIS data
dir_list = os.listdir("WEST_COAST_AIS")

# load grid into pandas dataframe
grid_file = pd.read_csv("GRIDS/SF_GRID_TEST.csv")

# establish new columns for the measurements and ROTR
grid_file["MIN"] = 0
grid_file["<.5"] = 0
grid_file["<1"] = 0
grid_file["1-2"] = 0
grid_file["2-3"] = 0
grid_file[">3"] = 0
grid_file["<.5_crossing"] = 0
grid_file["<.5_overtaking"] = 0
grid_file["<.5_headon"] = 0
grid_file["<1_crossing"] = 0
grid_file["<1_overtaking"] = 0
grid_file["<1_headon"] = 0

# loop through files in the AIS directory
for file in dir_list:

    # select which files in directory
    if "AIS_2021_" in file:
        # load AIS csv into pandas dataframe
        AIS_data_raw = pd.read_csv(f"WEST_COAST_AIS/{file}", encoding="UTF-8")
        # initiate timer for process time
        timer_start = datetime.datetime.now()
        # loop through grid points
        for row in grid_file.index:

            # process check read-out
            if row % 3000 == 0:
                print(row)

            # set default values for counters and for a starting minimum distance
            min = 10
            halfmi = 0
            one = 0
            two = 0
            three = 0
            threeplus = 0
            halfmi_x = 0
            halfmi_over = 0
            halfmi_head = 0
            mi_x = 0
            mi_over = 0
            mi_head = 0

            # define search area surrounding grid point ~6 nautical miles
            lat_c = grid_file["LAT"][row]
            lon_c = grid_file["LON"][row]
            lat_tl = lat_c + .0667
            lat_br = lat_c - .0667
            lon_tl = lon_c - .0667
            lon_br = lon_c + .0667

            # load AIS data for the search area
            AIS_data = AIS_data_raw[AIS_data_raw["LAT"] > lat_br]
            AIS_data = AIS_data[AIS_data["LAT"] < lat_tl]
            AIS_data = AIS_data[AIS_data["LON"] > lon_tl]
            AIS_data = AIS_data[AIS_data["LON"] < lon_br]

            # sort by datetime and reset index
            AIS_data = AIS_data.sort_values(["BaseDateTime"], ascending=[True]).reset_index(drop=True).reset_index()
            AIS_data.set_index("index", inplace=True)

            # create empty MMSI index to capture observed vessel pairs
            MMSI_index = []

            # set a minute index of all unique timestamps loaded for grid point
            min_index = AIS_data["BaseDateTime"].unique()

            # set a minimum minute reference
            min_ref = "0:00"

            # if the timestamp is greater than an hour from the reference, empty the observation index and capture time
            for minute in min_index:
                if abs((pd.to_datetime(minute) - pd.to_datetime(min_ref)).total_seconds())/60 > 20:
                    MMSI_index = []
                    min_ref = minute

                # while looping through the min_index, grab only those values that are the same time
                temp_df = AIS_data[AIS_data["BaseDateTime"] == minute]

                # loop through the vessels captured and compare to every other vessel
                for vessel1 in temp_df.index:
                    for vessel2 in temp_df.index:
                        # the vessels cannot be compared to themselves
                        if temp_df["MMSI"][vessel1] != temp_df["MMSI"][vessel2] and temp_df["SOG"][vessel1] > 0.4 and temp_df["SOG"][vessel2] > 0.4:
                            # check if vessels are not in the MMSI_index
                            if (temp_df["MMSI"][vessel1], temp_df["MMSI"][vessel2]) not in MMSI_index and (temp_df["MMSI"][vessel2], temp_df["MMSI"][vessel1]) not in MMSI_index:

                                # if not in the index, add the pair
                                MMSI_index.append((temp_df["MMSI"][vessel1], temp_df["MMSI"][vessel2]))

                                # calc distance between vessels for CPA
                                dist = gp((temp_df["LAT"][vessel1], temp_df["LON"][vessel1]), (temp_df["LAT"][vessel2], temp_df["LON"][vessel2])).nm

                                # compare to min value, update if lower
                                if dist < min:
                                    min = dist

                                # if distance is less than half a nautical mile, add to counter
                                if dist < .5:
                                    halfmi += 1

                                    if temp_df["COG"][vessel1] >= 0 and temp_df["COG"][vessel2] >=0:

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

                                            if temp_df["SOG"][vessel1] > 0 and temp_df["SOG"][vessel2] > 0:

                                                # if the SOG is above 0, then below will convert heading to a range 180/-180 in order to average.
                                                A = temp_df["COG"][vessel1]

                                                B = temp_df["COG"][vessel2]

                                                # average heading and convert back to 360
                                                AVG_heading = (A + B)/2

                                                # if AVG_heading is in one of 8 sectors, then determine what criteria of lat/lon differences are needed for the tailing vessel
                                                    ### if North
                                                if AVG_heading >= 337.7 and AVG_heading < 22.5:
                                                    if temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] > 0:
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 1:
                                                            halfmi_over += 1
                                                    elif temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] > 0:
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 1:
                                                            halfmi_over += 1
                                                    ### if North East
                                                elif AVG_heading >= 22.5 and AVG_heading < 67.5:
                                                    if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] > 0) and (temp_df["LON"][vessel1] - temp_df["LON"][vessel2] > 0):
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 1:
                                                            halfmi_over += 1
                                                    elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] > 0) and (temp_df["LON"][vessel2] - temp_df["LON"][vessel1] > 0):
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 1:
                                                            halfmi_over += 1
                                                    ### if East
                                                elif AVG_heading >= 67.5 and AVG_heading < 112.5:
                                                    if temp_df["LON"][vessel1] - temp_df["LON"][vessel2] > 0:
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 1:
                                                            halfmi_over += 1
                                                    elif temp_df["LON"][vessel2] - temp_df["LON"][vessel1] > 0:
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 1:
                                                            halfmi_over += 1
                                                    ### if South East
                                                elif AVG_heading >= 112.5 and AVG_heading < 157.5:
                                                    if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] < 0) and (temp_df["LON"][vessel1] - temp_df["LON"][vessel2] > 0):
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 1:
                                                            halfmi_over += 1
                                                    elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] < 0) and (temp_df["LON"][vessel2] - temp_df["LON"][vessel1] > 0):
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 1:
                                                            halfmi_over += 1
                                                    ### if South
                                                elif AVG_heading >= 157.5 and AVG_heading < 202.5:
                                                    if temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] < 0:
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 1:
                                                            halfmi_over += 1
                                                    elif temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] < 0:
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 1:
                                                            halfmi_over += 1
                                                    ### if South West
                                                elif AVG_heading >= 202.5 and AVG_heading < 247.5:
                                                    if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] < 0) and (temp_df["LON"][vessel1] - temp_df["LON"][vessel2] < 0):
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 1:
                                                            halfmi_over += 1
                                                    elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] < 0) and (temp_df["LON"][vessel2] - temp_df["LON"][vessel1] < 0):
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 1:
                                                            halfmi_over += 1
                                                    ### if West
                                                elif AVG_heading >= 247.5 and AVG_heading < 292.5:
                                                    if temp_df["LON"][vessel1] - temp_df["LON"][vessel2] < 0:
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 1:
                                                            halfmi_over += 1
                                                    elif temp_df["LON"][vessel2] - temp_df["LON"][vessel1] < 0:
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 1:
                                                            halfmi_over += 1
                                                    ### if North West
                                                elif AVG_heading >= 292.5 and AVG_heading < 337.5:
                                                    if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] > 0) and (temp_df["LON"][vessel1] - temp_df["LON"][vessel2] < 0):
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1] + 1:
                                                            halfmi_over += 1
                                                    elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] > 0) and (temp_df["LON"][vessel2] - temp_df["LON"][vessel1] < 0):
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2] + 1:
                                                            halfmi_over += 1



                                        if delta > 45 and delta < 135: # crossing

                                            v1_2 = gd.WGS84.Inverse(temp_df["LAT"][vessel1], temp_df["LON"][vessel1], temp_df["LAT"][vessel2], temp_df["LON"][vessel2])['azi1']
                                            v2_1 = gd.WGS84.Inverse(temp_df["LAT"][vessel2], temp_df["LON"][vessel2], temp_df["LAT"][vessel1], temp_df["LON"][vessel1])['azi1']

                                            if v1_2 < 0:
                                                v1_2_hi = v1_2 + 360
                                            else:
                                                v1_2_hi = v1_2

                                            if v2_1 < 0:
                                                v2_1_hi = v2_1 + 360
                                            else:
                                                v2_1_hi = v2_1

                                            if v1_2_hi > temp_df["COG"][vessel1]:
                                                larger_head1 = v1_2_hi
                                                smaller_head1 = temp_df["COG"][vessel1]
                                            else:
                                                larger_head1 = temp_df["COG"][vessel1]
                                                smaller_head1 = v1_2_hi

                                            if v2_1_hi > temp_df["COG"][vessel2]:
                                                larger_head2 = v2_1_hi
                                                smaller_head2 = temp_df["COG"][vessel2]
                                            else:
                                                larger_head2 = temp_df["COG"][vessel2]
                                                smaller_head2 = v2_1_hi

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

                                        if delta >= 135: # head on
                                                halfmi_head += 1


                                elif dist < 1:
                                    one += 1

                                    if temp_df["COG"][vessel1] >= 0 and temp_df["COG"][vessel2] >= 0:

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

                                        if delta <= 45:  # overtaking

                                            if temp_df["SOG"][vessel1] > 0 and temp_df["SOG"][vessel2] > 0:

                                                # if the SOG is above 0, then below will convert heading to a range 180/-180 in order to average.
                                                A = temp_df["COG"][vessel1]

                                                B = temp_df["COG"][vessel2]

                                                # average heading and convert back to 360
                                                AVG_heading = (A + B) / 2

                                                # if AVG_heading is in one of 8 sectors, then determine what criteria of lat/lon differences are needed for the tailing vessel
                                                ### if North
                                                if AVG_heading >= 337.7 and AVG_heading < 22.5:
                                                    if temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] > 0:
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1]:
                                                            mi_over += 1
                                                    elif temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] > 0:
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2]:
                                                            mi_over += 1
                                                    ### if North East
                                                elif AVG_heading >= 22.5 and AVG_heading < 67.5:
                                                    if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] > 0) and (
                                                            temp_df["LON"][vessel1] - temp_df["LON"][vessel2] > 0):
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1]:
                                                            mi_over += 1
                                                    elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] > 0) and (
                                                            temp_df["LON"][vessel2] - temp_df["LON"][vessel1] > 0):
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2]:
                                                            mi_over += 1
                                                    ### if East
                                                elif AVG_heading >= 67.5 and AVG_heading < 112.5:
                                                    if temp_df["LON"][vessel1] - temp_df["LON"][vessel2] > 0:
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1]:
                                                            mi_over += 1
                                                    elif temp_df["LON"][vessel2] - temp_df["LON"][vessel1] > 0:
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2]:
                                                            mi_over += 1
                                                    ### if South East
                                                elif AVG_heading >= 112.5 and AVG_heading < 157.5:
                                                    if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] < 0) and (
                                                            temp_df["LON"][vessel1] - temp_df["LON"][vessel2] > 0):
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1]:
                                                            mi_over += 1
                                                    elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] < 0) and (
                                                            temp_df["LON"][vessel2] - temp_df["LON"][vessel1] > 0):
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2]:
                                                            mi_over += 1
                                                    ### if South
                                                elif AVG_heading >= 157.5 and AVG_heading < 202.5:
                                                    if temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] < 0:
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1]:
                                                            mi_over += 1
                                                    elif temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] < 0:
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2]:
                                                            mi_over += 1
                                                    ### if South West
                                                elif AVG_heading >= 202.5 and AVG_heading < 247.5:
                                                    if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] < 0) and (
                                                            temp_df["LON"][vessel1] - temp_df["LON"][vessel2] < 0):
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1]:
                                                            mi_over += 1
                                                    elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] < 0) and (
                                                            temp_df["LON"][vessel2] - temp_df["LON"][vessel1] < 0):
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2]:
                                                            mi_over += 1
                                                    ### if West
                                                elif AVG_heading >= 247.5 and AVG_heading < 292.5:
                                                    if temp_df["LON"][vessel1] - temp_df["LON"][vessel2] < 0:
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1]:
                                                            mi_over += 1
                                                    elif temp_df["LON"][vessel2] - temp_df["LON"][vessel1] < 0:
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2]:
                                                            mi_over += 1
                                                    ### if North West
                                                elif AVG_heading >= 292.5 and AVG_heading < 337.5:
                                                    if (temp_df["LAT"][vessel1] - temp_df["LAT"][vessel2] > 0) and (
                                                            temp_df["LON"][vessel1] - temp_df["LON"][vessel2] < 0):
                                                        if temp_df["SOG"][vessel2] > temp_df["SOG"][vessel1]:
                                                            mi_over += 1
                                                    elif (temp_df["LAT"][vessel2] - temp_df["LAT"][vessel1] > 0) and (
                                                            temp_df["LON"][vessel2] - temp_df["LON"][vessel1] < 0):
                                                        if temp_df["SOG"][vessel1] > temp_df["SOG"][vessel2]:
                                                            mi_over += 1

                                        if delta > 45 and delta < 135:  # crossing

                                            v1_2 = gd.WGS84.Inverse(temp_df["LAT"][vessel1], temp_df["LON"][vessel1],
                                                                    temp_df["LAT"][vessel2], temp_df["LON"][vessel2])[
                                                'azi1']
                                            v2_1 = gd.WGS84.Inverse(temp_df["LAT"][vessel2], temp_df["LON"][vessel2],
                                                                    temp_df["LAT"][vessel1], temp_df["LON"][vessel1])[
                                                'azi1']

                                            if v1_2 < 0:
                                                v1_2_hi = v1_2 + 360
                                            else:
                                                v1_2_hi = v1_2

                                            if v2_1 < 0:
                                                v2_1_hi = v2_1 + 360
                                            else:
                                                v2_1_hi = v2_1

                                            if v1_2_hi > temp_df["COG"][vessel1]:
                                                larger_head1 = v1_2_hi
                                                smaller_head1 = temp_df["COG"][vessel1]
                                            else:
                                                larger_head1 = temp_df["COG"][vessel1]
                                                smaller_head1 = v1_2_hi

                                            if v2_1_hi > temp_df["COG"][vessel2]:
                                                larger_head2 = v2_1_hi
                                                smaller_head2 = temp_df["COG"][vessel2]
                                            else:
                                                larger_head2 = temp_df["COG"][vessel2]
                                                smaller_head2 = v2_1_hi

                                            if larger_head1 - smaller_head1 > 180:
                                                delta1 = 360 - (larger_head1 - smaller_head1)
                                            else:
                                                delta1 = larger_head1 - smaller_head1

                                            if larger_head2 - smaller_head2 > 180:
                                                delta2 = 360 - (larger_head2 - smaller_head2)
                                            else:
                                                delta2 = larger_head2 - smaller_head2

                                            if delta1 < 90 and delta2 < 90:
                                                mi_x += 1

                                        if delta >= 135:  # head on
                                            mi_head += 1
                                elif dist < 2:
                                    two += 1
                                elif dist < 3:
                                    three += 1
                                else:
                                    threeplus += 1



            grid_file.loc[row, "MIN"] = min
            grid_file.loc[row, "<.5"] = halfmi
            grid_file.loc[row, "<1"] = one
            grid_file.loc[row, "1-2"] = two
            grid_file.loc[row, "2-3"] = three
            grid_file.loc[row, ">3"] = threeplus
            grid_file.loc[row, "<.5_crossing"] = halfmi_x
            grid_file.loc[row, "<.5_overtaking"] = halfmi_over
            grid_file.loc[row, "<.5_headon"] = halfmi_head
            grid_file.loc[row, "<1_crossing"] = mi_x
            grid_file.loc[row, "<1_overtaking"] = mi_over
            grid_file.loc[row, "<1_headon"] = mi_head


        file_split = file.split(".")

        grid_file.to_csv(f"Vessel_Interaction_West/SF/Vessel_Interaction_{file_split[0]}.csv", index=False)
        print(file_split[0])
        print(f"{abs((timer_start - datetime.datetime.now()).total_seconds()) / 60} minutes")