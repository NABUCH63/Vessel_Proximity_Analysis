import os

import pandas as pd

folder = "Vessel_Interaction_GL"
output = "GL_AVG_DAILY_INTERACTIONS_MAX_MONTH_2021.csv"
dir_list = os.listdir(f"C:/Users/Nodak/PycharmProjects/AIS_FILE_GRAB/{folder}")

month_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]


for month in month_list:
    n = 1

    for file in dir_list:

        if f"Vessel_Interaction_AIS_2021_{month}" in file:

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

                    if initial_grid.loc[i, "MIN"] > temp_df.loc[i, "MIN"]:

                        initial_grid.loc[i, "MIN"] = temp_df.loc[i, "MIN"]

                n += 1

    initial_grid.loc[:, "MIN"] = initial_grid.loc[:, "MIN"]/n
    initial_grid.loc[:, "<.5"] = initial_grid.loc[:, "<.5"]/n
    initial_grid.loc[:, "<1"] = initial_grid.loc[:, "<1"]/n
    initial_grid.loc[:, "1-2"] = initial_grid.loc[:, "1-2"]/n
    initial_grid.loc[:, "2-3"] = initial_grid.loc[:, "2-3"]/n
    initial_grid.loc[:, ">3"] = initial_grid.loc[:, ">3"]/n

    if month == "01":

        final_grid = initial_grid.copy()
        final_grid["Busiest_Month"] = 0
        final_grid["Busiest_Month_Interactions"] = 0


    for t in initial_grid.index:

        if (float(initial_grid.loc[t, "<.5"]) + float(initial_grid.loc[t, "<1"]) + float(initial_grid.loc[t, "1-2"]) + float(initial_grid.loc[t, "2-3"]) + float(initial_grid.loc[t, ">3"])) > (float(final_grid.loc[t, "Busiest_Month_Interactions"])):
            final_grid.loc[t, "Busiest_Month"] = month
            final_grid.loc[t, "Busiest_Month_Interactions"] = (float(initial_grid.loc[t, "<.5"]) + float(initial_grid.loc[t, "<1"]) + float(initial_grid.loc[t, "1-2"]) + float(initial_grid.loc[t, "2-3"]) + float(initial_grid.loc[t, ">3"]))

        if final_grid.loc[t, "<.5"] < initial_grid.loc[t, "<.5"]:
            final_grid.loc[t, "<.5"] = initial_grid.loc[t, "<.5"]
        if final_grid.loc[t, "<1"] < initial_grid.loc[t, "<1"]:
            final_grid.loc[t, "<1"] = initial_grid.loc[t, "<1"]
        if final_grid.loc[t, "1-2"] < initial_grid.loc[t, "1-2"]:
            final_grid.loc[t, "1-2"] = initial_grid.loc[t, "1-2"]
        if final_grid.loc[t, "2-3"] < initial_grid.loc[t, "2-3"]:
            final_grid.loc[t, "2-3"] = initial_grid.loc[t, "2-3"]
        if final_grid.loc[t, ">3"] < initial_grid.loc[t, ">3"]:
            final_grid.loc[t, ">3"] = initial_grid.loc[t, ">3"]
        if final_grid.loc[t, "MIN"] > initial_grid.loc[t, "MIN"]:
            final_grid.loc[t, "MIN"] = initial_grid.loc[t, "MIN"]



final_grid.rename(columns={"<.5": "0-.5nm", "<1": ".5-1nm", "1-2": "1-2nm", "2-3": "2-3nm", ">3": "3-12nm"}, inplace=True)

final_grid.to_csv(output, index=False)







