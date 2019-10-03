from flask import Flask, render_template, request
from time import strftime, time
from datetime import datetime
import pytz
import requests
import pandas as pd 
from function import make_map
import csv
import json
from waitress import serve

app = Flask(__name__, static_url_path="/static")


@app.route("/")
def index():
    """Return the main page."""
    with open('station_name.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        # for row in reader:
        #     print(row)
        tz = pytz.timezone('US/Pacific')
        LA_now = datetime.now(tz)
        
        time_str = LA_now.strftime("%m/%d/%Y %H:%M")
        print(time_str)
        # stations = ["3047", "3005", "3023"]
        return render_template("index.html", time_info=time_str, reader=reader)

# @app.route("/")
# def index():
#     """Return the main page."""
#     time_str = strftime("%m/%d/%Y %H:%M")
#     print(time_str)
#     restaurants = ["Din Tai Fung", "Rocco's", "Chipotle"]
#     return render_template("index.html", time_info=time_str, restaurants=restaurants)
# @app.route('/')
# def index():
#     folium_map = make_map()
#     return folium_map._repr_html_()


# if __name__ == '__main__':
#     app.run(debug=True)

@app.route("/get_results", methods=["POST"])

def get_results():
    with open('station_name.json') as json_file:
        stations = json.load(json_file)

        data = request.form
        print(data)

        station = data["station"]

        # stations = {}
        # for row in reader:
        #     kiosk_id= row['kioskId']
        #     lat = row['latitude']
        #     lng = row['longitude']
        #     stations[kiosk_id] = (lat, lng)

        lat, lng = stations[station]

    # live_station_df = get_live_station("https://bikeshare.metro.net/stations/json/")
    # print(live_station_df)

    # # answer = should_make_transaction(user_id)
    # return render_template("results.html", station=station, lat=lat, lng=lng)
        folium_map = make_map(stations[station])
        return folium_map._repr_html_()


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)

# def should_make_transaction(user_id):
#     return False

# def get_live_station(url):
    
#     response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
#     stations = response.json()
    
#     output = []
    
#     for station in stations['features']:
#         dict_keys = ['kioskId', 'bikesAvailable', 'docksAvailable', 'name', 'latitude', 'longitude']
#         data = {k : station['properties'][k] for k in dict_keys}
#         data['time'] = time()
#         output.append(data)

#     return pd.DataFrame(output)