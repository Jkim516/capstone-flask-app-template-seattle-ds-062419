import requests
import pandas as pd 
import folium 
from folium.plugins import MiniMap
import pickle
from time import time


def get_live_station(url):
    
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    stations = response.json()
    
    output = []
    
    for station in stations['features']:
        dict_keys = ['kioskId', 'bikesAvailable', 'docksAvailable', 'name', 'latitude', 'longitude']
        data = {k : station['properties'][k] for k in dict_keys}
        data['time'] = pd.to_datetime('today')
        output.append(data)

    return pd.DataFrame(output)


def normalize_demand_number(record):
    if record['y_hat'] >= 4.5:
        return round(record['y_hat']) * 2.5
    elif record['y_hat'] >= 4:
        return round(record['y_hat']) * 2
    elif record['y_hat'] >= 3:
        return round(record['y_hat']) * 2
    elif record['y_hat'] >= 1:
        return round(record['y_hat']) * 3
    elif record['y_hat'] >= 0.7:
        return round(record['y_hat']) * 2
    elif record['y_hat'] >= 0.4:
        return round(record['y_hat']) * 1
    else:
        return 0

def nexthour(record):
    if record['bikesAvailable'] - record['demand'] >= 0:
        return record['bikesAvailable'] - record['demand']
    else:
        return 0

def make_map(station):
    with open('station_pred_df1.pickle', 'rb') as f:
        station_pred_df1 = pickle.load(f)

    live_station_df = get_live_station("https://bikeshare.metro.net/stations/json/")

    # change time feature into str and take first 10 character.
    # live_station_df.time = live_station_df.time.astype(str)
    # live_station_df.time = live_station_df.time.str[:10]
    live_station_df['time'] = live_station_df['time'].astype('datetime64[s]')
    
    # convert unix timestamp to Y/M/D %H/%M/%S format
    # live_station_df['time'] = pd.to_datetime(live_station_df['time'], unit='s')

    # change name of time feature to ds and set it to index
    # replace minutes and seconds to 0 
    live_station_df.rename(columns={'time':'ds'}, inplace=True)
    live_station_df.set_index('ds', inplace=True)
    live_station_df.index = live_station_df.index.map(lambda x: x.replace(second=0))
    live_station_df.index = live_station_df.index.map(lambda x: x.replace(minute=0))

    live_station_df.kioskId = live_station_df.kioskId.astype(str)
    live_station_df.reset_index(inplace=True)
    live_station_df['id'] = live_station_df.ds.astype(str) + '-' + live_station_df.kioskId

    # Take first 4 character in station feature
    station_pred_df1.station = station_pred_df1.station.str[:4]
    station_pred_df1['id'] = station_pred_df1.ds.astype(str) + '-' + station_pred_df1.station
    station_pred_df1.set_index('ds', inplace=True)

    merge_live_pred_df = station_pred_df1.merge(live_station_df, on='id')
    merge_live_pred_df['demand'] = merge_live_pred_df.apply(normalize_demand_number, axis=1)
    merge_live_pred_df['nextHour'] = merge_live_pred_df.apply(nexthour, axis=1)


    lat, lng = station
    minimap = MiniMap(toggle_display=True, width=300, height=150, zoom_animation=True, zoom_level_offset=-6, position='topleft')
    df = merge_live_pred_df
    map = folium.Map(location=[lat, lng],
                    zoom_start=21,
                    tiles='OpenStreetMap').add_child(minimap)


    for lat, lon, Name, Available, Opendocks, Next_hr_remaining, in zip(df['latitude'], 
                                                                        df['longitude'], 
                                                                        df['name'], 
                                                                        df['bikesAvailable'], 
                                                                        df['docksAvailable'], 
                                                                        df['nextHour']):
        folium.Marker([lat,lon], 
                  popup=(str(Name).capitalize() + '<br>'
                         '<br><b>Available: </b>' + str(Available) + '<br>'
                         '<br><b>Opendocks: </b>' + str(Opendocks) + '<br>'
                        '<br><b>Remaining Next Hour:</b> ' + str(Next_hr_remaining)),
                  icon=folium.Icon(color='green')).add_to(map)

    return map

