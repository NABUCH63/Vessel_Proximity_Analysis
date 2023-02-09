import os
import pandas as pd

folder = "Result"
output1 = "SF1_Test_Annual_AVG_Daily_Vessel_Interaction_2021.csv"
output2 = "SF1_Test_Annual_Max_Daily_Vessel_Interaction_2021.csv"

dir_list = os.listdir(f"C:/Users/Nodak/Documents/GitHub/Vessel_Proximity_Analysis/{folder}")

n = 1

for file in dir_list:
    print(n)
    print(file)
    if n == 1:
        temp_df = pd.read_csv(f"C:/Users/Nodak/Documents/GitHub/Vessel_Proximity_Analysis/{folder}/{file}")
        initial_grid = temp_df.copy()
        max_grid = temp_df.copy()
        n += 1

    else:
        temp_df = pd.read_csv(f"C:/Users/Nodak/Documents/GitHub/Vessel_Proximity_Analysis/{folder}/{file}")
        for i in initial_grid.index:
            initial_grid.loc[i, "Total_Interactions"] += temp_df.loc[i, "Total_Interactions"]
            initial_grid.loc[i, "crossing"] += temp_df.loc[i, "crossing"]
            initial_grid.loc[i, "headon"] += temp_df.loc[i, "headon"]
            initial_grid.loc[i, "overtaking"] += temp_df.loc[i, "overtaking"]
            initial_grid.loc[i, "Passenger_Interactions"] += temp_df.loc[i, "Passenger_Interactions"]
            initial_grid.loc[i, "pass_crossing"] += temp_df.loc[i, "pass_crossing"]
            initial_grid.loc[i, "pass_headon"] += temp_df.loc[i, "pass_headon"]
            initial_grid.loc[i, "pass_overtaking"] += temp_df.loc[i, "pass_overtaking"]
            initial_grid.loc[i, "pass_flagged"] += temp_df.loc[i, "pass_flagged"]
            initial_grid.loc[i, "CT_Interactions"] += temp_df.loc[i, "CT_Interactions"]
            initial_grid.loc[i, "CT_crossing"] += temp_df.loc[i, "CT_crossing"]
            initial_grid.loc[i, "CT_headon"] += temp_df.loc[i, "CT_headon"]
            initial_grid.loc[i, "CT_overtaking"] += temp_df.loc[i, "CT_overtaking"]
            initial_grid.loc[i, "CT_flagged"] += temp_df.loc[i, "CT_flagged"]
            initial_grid.loc[i, "Flagged_Interactions"] += temp_df.loc[i, "Flagged_Interactions"]
            initial_grid.loc[i, "flagged_crossing"] += temp_df.loc[i, "flagged_crossing"]
            initial_grid.loc[i, "flagged_headon"] += temp_df.loc[i, "flagged_headon"]
            initial_grid.loc[i, "flagged_overtaking"] += temp_df.loc[i, "flagged_overtaking"]
            initial_grid.loc[i, "Nonrec_Interactions"] += temp_df.loc[i, "Nonrec_Interactions"]
            initial_grid.loc[i, "Flagged_Nonrec_Interactions"] += temp_df.loc[i, "Flagged_Nonrec_Interactions"]
            initial_grid.loc[i, "nonrec_crossing"] += temp_df.loc[i, "nonrec_crossing"]
            initial_grid.loc[i, "nonrec_overtaking"] += temp_df.loc[i, "nonrec_overtaking"]
            initial_grid.loc[i, "nonrec_headon"] += temp_df.loc[i, "nonrec_headon"]



        n += 1

        for x in max_grid.index:
            if max_grid.loc[x, "Total_Interactions"] < temp_df.loc[x, "Total_Interactions"]:
                max_grid.loc[x, "Total_Interactions"] = temp_df.loc[x, "Total_Interactions"]
            if max_grid.loc[i, "crossing"] < temp_df.loc[i, "crossing"]:
                max_grid.loc[i, "crossing"] = temp_df.loc[i, "crossing"]
            if max_grid.loc[i, "headon"] < temp_df.loc[i, "headon"]:
                max_grid.loc[i, "headon"] = temp_df.loc[i, "headon"]
            if max_grid.loc[i, "overtaking"] < temp_df.loc[i, "overtaking"]:
                max_grid.loc[i, "overtaking"] = temp_df.loc[i, "overtaking"]
            if max_grid.loc[x, "Passenger_Interactions"] < temp_df.loc[x, "Passenger_Interactions"]:
                max_grid.loc[x, "Passenger_Interactions"] = temp_df.loc[x, "Passenger_Interactions"]
            if max_grid.loc[i, "pass_crossing"] < temp_df.loc[i, "pass_crossing"]:
                max_grid.loc[i, "pass_crossing"] = temp_df.loc[i, "pass_crossing"]
            if max_grid.loc[i, "pass_headon"] < temp_df.loc[i, "pass_headon"]:
                max_grid.loc[i, "pass_headon"] = temp_df.loc[i, "pass_headon"]
            if max_grid.loc[i, "pass_overtaking"] < temp_df.loc[i, "pass_overtaking"]:
                max_grid.loc[i, "pass_overtaking"] = temp_df.loc[i, "pass_overtaking"]
            if max_grid.loc[x, "CT_Interactions"] < temp_df.loc[x, "CT_Interactions"]:
                max_grid.loc[x, "CT_Interactions"] = temp_df.loc[x, "CT_Interactions"]
            if max_grid.loc[i, "CT_crossing"] < temp_df.loc[i, "CT_crossing"]:
                max_grid.loc[i, "CT_crossing"] = temp_df.loc[i, "CT_crossing"]
            if max_grid.loc[i, "CT_headon"] < temp_df.loc[i, "CT_headon"]:
                max_grid.loc[i, "CT_headon"] = temp_df.loc[i, "CT_headon"]
            if max_grid.loc[i, "CT_overtaking"] < temp_df.loc[i, "CT_overtaking"]:
                max_grid.loc[i, "CT_overtaking"] = temp_df.loc[i, "CT_overtaking"]
            if max_grid.loc[x, "Flagged_Interactions"] < temp_df.loc[x, "Flagged_Interactions"]:
                max_grid.loc[x, "Flagged_Interactions"] = temp_df.loc[x, "Flagged_Interactions"]
            if max_grid.loc[i, "flagged_crossing"] < temp_df.loc[i, "flagged_crossing"]:
                max_grid.loc[i, "flagged_crossing"] = temp_df.loc[i, "flagged_crossing"]
            if max_grid.loc[i, "flagged_headon"] < temp_df.loc[i, "flagged_headon"]:
                max_grid.loc[i, "flagged_headon"] = temp_df.loc[i, "flagged_headon"]
            if max_grid.loc[i, "flagged_overtaking"] < temp_df.loc[i, "flagged_overtaking"]:
                max_grid.loc[i, "flagged_overtaking"] = temp_df.loc[i, "flagged_overtaking"]
            if max_grid.loc[i, "pass_flagged"] < temp_df.loc[i, "pass_flagged"]:
                max_grid.loc[i, "pass_flagged"] = temp_df.loc[i, "pass_flagged"]
            if max_grid.loc[i, "CT_flagged"] < temp_df.loc[i, "CT_flagged"]:
                max_grid.loc[i, "CT_flagged"] = temp_df.loc[i, "CT_flagged"]
            if max_grid.loc[i, "Nonrec_Interactions"] < temp_df.loc[i, "Nonrec_Interactions"]:
                max_grid.loc[i, "Nonrec_Interactions"] = temp_df.loc[i, "Nonrec_Interactions"]
            if max_grid.loc[i, "Flagged_Nonrec_Interactions"] < temp_df.loc[i, "Flagged_Nonrec_Interactions"]:
                max_grid.loc[i, "Flagged_Nonrec_Interactions"] = temp_df.loc[i, "Flagged_Nonrec_Interactions"]
            if max_grid.loc[i, "nonrec_crossing"] < temp_df.loc[i, "nonrec_crossing"]:
                max_grid.loc[i, "nonrec_crossing"] = temp_df.loc[i, "nonrec_crossing"]
            if max_grid.loc[i, "nonrec_overtaking"] < temp_df.loc[i, "nonrec_overtaking"]:
                max_grid.loc[i, "nonrec_overtaking"] = temp_df.loc[i, "nonrec_overtaking"]
            if max_grid.loc[i, "nonrec_headon"] < temp_df.loc[i, "nonrec_headon"]:
                max_grid.loc[i, "nonrec_headon"] = temp_df.loc[i, "nonrec_headon"]



initial_grid.loc[:, "Total_Interactions"] = initial_grid.loc[:, "Total_Interactions"]/n
initial_grid.loc[:, "overtaking"] = initial_grid.loc[:, "overtaking"]/n
initial_grid.loc[:, "crossing"] = initial_grid.loc[:, "crossing"]/n
initial_grid.loc[:, "headon"] = initial_grid.loc[:, "headon"]/n
initial_grid.loc[:, "Passenger_Interactions"] = initial_grid.loc[:, "Passenger_Interactions"]/n
initial_grid.loc[:, "pass_overtaking"] = initial_grid.loc[:, "pass_overtaking"]/n
initial_grid.loc[:, "pass_crossing"] = initial_grid.loc[:, "pass_crossing"]/n
initial_grid.loc[:, "pass_headon"] = initial_grid.loc[:, "pass_headon"]/n
initial_grid.loc[:, "pass_flagged"] = initial_grid.loc[:, "pass_flagged"]/n
initial_grid.loc[:, "CT_Interactions"] = initial_grid.loc[:, "CT_Interactions"]/n
initial_grid.loc[:, "CT_overtaking"] = initial_grid.loc[:, "CT_overtaking"]/n
initial_grid.loc[:, "CT_crossing"] = initial_grid.loc[:, "CT_crossing"]/n
initial_grid.loc[:, "CT_headon"] = initial_grid.loc[:, "CT_headon"]/n
initial_grid.loc[:, "CT_flagged"] = initial_grid.loc[:, "CT_flagged"]/n
initial_grid.loc[:, "Flagged_Interactions"] = initial_grid.loc[:, "Flagged_Interactions"]/n
initial_grid.loc[:, "flagged_overtaking"] = initial_grid.loc[:, "flagged_overtaking"]/n
initial_grid.loc[:, "flagged_crossing"] = initial_grid.loc[:, "flagged_crossing"]/n
initial_grid.loc[:, "flagged_headon"] = initial_grid.loc[:, "flagged_headon"]/n
initial_grid.loc[:, "Nonrec_Interactions"] = initial_grid.loc[:, "Nonrec_Interactions"]/n
initial_grid.loc[:, "Flagged_Nonrec_Interactions"] = initial_grid.loc[:, "Flagged_Nonrec_Interactions"]/n
initial_grid.loc[:, "nonrec_crossing"] = initial_grid.loc[:, "nonrec_crossing"]/n
initial_grid.loc[:, "nonrec_overtaking"] = initial_grid.loc[:, "nonrec_overtaking"]/n
initial_grid.loc[:, "nonrec_headon"] = initial_grid.loc[:, "nonrec_headon"]/n

initial_grid.to_csv(f"{output1}", index=False)
max_grid.to_csv(f"{output2}", index=False)







