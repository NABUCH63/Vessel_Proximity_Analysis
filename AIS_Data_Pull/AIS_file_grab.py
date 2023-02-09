import datetime as dt
import os
import requests
from bs4 import BeautifulSoup as BS
import pandas as pd

url = 'https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2021/'

reqs = requests.get(url)
soup = BS(reqs.text, 'html.parser')
zip_list = []
for link in soup.find_all('a'):
    if link.get('href').endswith('.zip'):
        zip_list.append(link['href'])

# def list(raw_files):
#     n = 1
#     for f in raw_files:  # begins input loop of above defined list
#         if f"_{month}_" in f:
#             data = pd.read_csv(f"{url}{f}")#, usecols = ['MMSI', 'IMO', 'BaseDateTime', 'LAT', 'LON', 'VesselType', 'COG', 'Heading', 'SOG', 'Draft', 'Length'])  # define your desired columns, add: (example:) ".query('VesselType in ['35', '1003']')" to further edit down to a desired user group/attribute
#             a = data[data["LAT"] <= 50.0]  # (TOP BOUND) define LAT/LON bounds
#             b = a[a["LAT"] >= 30.0]  # (BOTTOM BOUND)
#             c = b[b["LON"] >= -130.0]  # (LEFT BOUND)
#             d = c[c["LON"] <= -116.0]  # (RIGHT BOUND)
#             yield d  # finish generator loop
#             n += 1
#             print(n)

month_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
for i in zip_list:
    print(i)

    AIS_url = f"{url}{i}"  # concatenate all above data to a single list
    data = pd.read_csv(AIS_url, usecols = ['MMSI', 'BaseDateTime', 'LAT', 'LON', 'VesselType', 'COG', 'SOG'], encoding="UTF-8")  # define your desired columns, add: (example:) ".query('VesselType in ['35', '1003']')" to further edit down to a desired user group/attribute
    a = data[data["LAT"] <= 38.32]  # (TOP BOUND) define LAT/LON bounds
    b = a[a["LAT"] >= 37.20]  # (BOTTOM BOUND)
    c = b[b["LON"] >= -122.92]  # (LEFT BOUND)
    df = c[c["LON"] <= -121.25]  # (RIGHT BOUND)
    df = pd.DataFrame(df)
    df['BaseDateTime'] = df['BaseDateTime'].fillna('2000-01-01T00:00:00')
    df.drop(df[df['LAT'] == None].index, inplace=True)
    df.drop(df[df['LON'] == None].index, inplace=True)
    df.drop(df[df['LON'] > 0].index, inplace=True)
    df.drop(df[df['MMSI'] == None].index, inplace=True)
    df.drop(df[df['BaseDateTime'] == None].index, inplace=True)
    df.dropna(subset=['MMSI', 'BaseDateTime', 'LAT', 'LON'], inplace=True)
    df.replace({"BaseDateTime": {'T': ' '}}, regex=True, inplace=True)
    df["BaseDateTime"] = pd.to_datetime(df["BaseDateTime"]).dt.strftime("%H:%M:%S")
    df.replace({"IMO": {'IMO': ''}}, regex=True, inplace=True)  # replace 'T' in date string with ' '
    df['VesselType'] = df['VesselType'].fillna(0)
    df["LAT"] = df["LAT"].round(5)
    df["LON"] = df["LON"].round(5)
    df.drop_duplicates(subset=["MMSI", "BaseDateTime", "LAT", "LON"], inplace=True)

    name = i.split(".")
    df.to_csv(f"SF_AIS/{name[0]}.csv", index=False)  # output csv with all entries


