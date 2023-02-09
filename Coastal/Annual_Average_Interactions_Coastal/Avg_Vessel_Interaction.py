import os
import pandas as pd

folder = "Vessel_Interaction_West/test"
output1 = "Test_Annual_AVG_Daily_Vessel_Interaction_2021.csv"
output2 = "Test_Annual_Max_Daily_Vessel_Interaction_2021.csv"

dir_list = os.listdir(f"C:/Users/Nodak/PycharmProjects/AIS_FILE_GRAB/{folder}")

n = 1

for file in dir_list:
    print(n)
    print(file)
    if n == 1:
        temp_df = pd.read_csv(f"C:/Users/Nodak/PycharmProjects/AIS_FILE_GRAB/{folder}/{file}")
        initial_grid = temp_df.copy()
        max_grid = temp_df.copy()
        n += 1

    else:
        temp_df = pd.read_csv(f"C:/Users/Nodak/PycharmProjects/AIS_FILE_GRAB/{folder}/{file}")
        for i in initial_grid.index:
            initial_grid.loc[i, "<.5"] += temp_df.loc[i, "<.5"]
            initial_grid.loc[i, "<1"] += temp_df.loc[i, "<1"]
            initial_grid.loc[i, "1-2"] += temp_df.loc[i, "1-2"]
            initial_grid.loc[i, "2-3"] += temp_df.loc[i, "2-3"]
            initial_grid.loc[i, ">3"] += temp_df.loc[i, ">3"]
            initial_grid.loc[i, "<.5_crossing"] += temp_df.loc[i, "<.5_crossing"]
            initial_grid.loc[i, "<.5_headon"] += temp_df.loc[i, "<.5_headon"]
            initial_grid.loc[i, "<.5_overtaking"] += temp_df.loc[i, "<.5_overtaking"]
            initial_grid.loc[i, "<1_crossing"] += temp_df.loc[i, "<1_crossing"]
            initial_grid.loc[i, "<1_headon"] += temp_df.loc[i, "<1_headon"]
            initial_grid.loc[i, "<1_overtaking"] += temp_df.loc[i, "<1_overtaking"]

            if initial_grid.loc[i, "MIN"] > temp_df.loc[i, "MIN"]:
                initial_grid.loc[i, "MIN"] = temp_df.loc[i, "MIN"]
        n += 1

        for x in max_grid.index:
            if max_grid.loc[x, "<.5"] < temp_df.loc[x, "<.5"]:
                max_grid.loc[x, "<.5"] = temp_df.loc[x, "<.5"]
            if max_grid.loc[x, "<1"] < temp_df.loc[x, "<1"]:
                max_grid.loc[x, "<1"] = temp_df.loc[x, "<1"]
            if max_grid.loc[x, "1-2"] < temp_df.loc[x, "1-2"]:
                max_grid.loc[x, "1-2"] = temp_df.loc[x, "1-2"]
            if max_grid.loc[x, "2-3"] < temp_df.loc[x, "2-3"]:
                max_grid.loc[x, "2-3"] = temp_df.loc[x, "2-3"]
            if max_grid.loc[x, ">3"] < temp_df.loc[x, ">3"]:
                max_grid.loc[x, ">3"] = temp_df.loc[x, ">3"]
            if max_grid.loc[x, "MIN"] > temp_df.loc[x, "MIN"]:
                max_grid.loc[x, "MIN"] = temp_df.loc[x, "MIN"]
            if max_grid.loc[i, "<.5_crossing"] < temp_df.loc[i, "<.5_crossing"]:
                max_grid.loc[i, "<.5_crossing"] = temp_df.loc[i, "<.5_crossing"]
            if max_grid.loc[i, "<.5_headon"] < temp_df.loc[i, "<.5_headon"]:
                max_grid.loc[i, "<.5_headon"] = temp_df.loc[i, "<.5_headon"]
            if max_grid.loc[i, "<.5_overtaking"] < temp_df.loc[i, "<.5_overtaking"]:
                max_grid.loc[i, "<.5_overtaking"] = temp_df.loc[i, "<.5_overtaking"]
            if max_grid.loc[i, "<1_crossing"] < temp_df.loc[i, "<1_crossing"]:
                max_grid.loc[i, "<1_crossing"] = temp_df.loc[i, "<1_crossing"]
            if max_grid.loc[i, "<1_headon"] < temp_df.loc[i, "<1_headon"]:
                max_grid.loc[i, "<1_headon"] = temp_df.loc[i, "<1_headon"]
            if max_grid.loc[i, "<1_overtaking"] < temp_df.loc[i, "<1_overtaking"]:
                max_grid.loc[i, "<1_overtaking"] = temp_df.loc[i, "<1_overtaking"]


initial_grid.loc[:, "MIN"] = initial_grid.loc[:, "MIN"]/n
initial_grid.loc[:, "<.5"] = initial_grid.loc[:, "<.5"]/n
initial_grid.loc[:, "<1"] = initial_grid.loc[:, "<1"]/n
initial_grid.loc[:, "1-2"] = initial_grid.loc[:, "1-2"]/n
initial_grid.loc[:, "2-3"] = initial_grid.loc[:, "2-3"]/n
initial_grid.loc[:, ">3"] = initial_grid.loc[:, ">3"]/n
initial_grid.loc[:, "<.5_overtaking"] = initial_grid.loc[:, "<.5_overtaking"]/n
initial_grid.loc[:, "<.5_crossing"] = initial_grid.loc[:, "<.5_crossing"]/n
initial_grid.loc[:, "<.5_headon"] = initial_grid.loc[:, "<.5_headon"]/n
initial_grid.loc[:, "<1_overtaking"] = initial_grid.loc[:, "<1_overtaking"]/n
initial_grid.loc[:, "<1_crossing"] = initial_grid.loc[:, "<1_crossing"]/n
initial_grid.loc[:, "<1_headon"] = initial_grid.loc[:, "<1_headon"]/n





initial_grid.rename(columns={"<.5": "0-.5nm", "<1": ".5-1nm", "1-2": "1-2nm", "2-3": "2-3nm", ">3": "3-12nm"}, inplace=True)
max_grid.rename(columns={"<.5": "0-.5nm", "<1": ".5-1nm", "1-2": "1-2nm", "2-3": "2-3nm", ">3": "3-12nm"}, inplace=True)


initial_grid.to_csv(f"{output1}", index=False)
max_grid.to_csv(f"{output2}", index=False)







