import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
import datetime



def get_weather_data(latitude, longitude, start_date, end_date):
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = { 
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["temperature_2m", "surface_pressure", "precipitation", "relative_humidity_2m", "wind_direction_10m", "wind_speed_10m", "wind_gusts_10m", "cloud_cover", "visibility", "weather_code"],
            "start_date": start_date,
	        "end_date": end_date}
        
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        # print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        # print(f"Elevation {response.Elevation()} m asl")
        # print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
        # print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = [float (x) for x in hourly.Variables(0).ValuesAsNumpy()]
        hourly_surface_pressure = [float (x) for x in hourly.Variables(1).ValuesAsNumpy()]
        hourly_precipitation = [float (x) for x in hourly.Variables(2).ValuesAsNumpy()]
        hourly_relative_humidity_2m = [float (x) for x in hourly.Variables(3).ValuesAsNumpy()]
        hourly_wind_direction_10m = [float (x) for x in hourly.Variables(4).ValuesAsNumpy()]
        hourly_wind_speed_10m = [float (x) for x in hourly.Variables(5).ValuesAsNumpy()]
        hourly_wind_gusts_10m = [float (x) for x in hourly.Variables(6).ValuesAsNumpy()]
        hourly_cloud_cover = [float (x) for x in hourly.Variables(7).ValuesAsNumpy()]
        hourly_visibility = [float (x) for x in hourly.Variables(8).ValuesAsNumpy()]
        hourly_weather_code = [float (x) for x in hourly.Variables(9).ValuesAsNumpy()]

        date_range = pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        ).to_list()

        # print(dir(date_range[0]))

        hourly_data = {}
        for i in range(len(date_range)):
            hourly_data[date_range[i]] = {"temperature_2m" : hourly_temperature_2m[i], "surface_pressure" : hourly_surface_pressure[i], "precipitation" : hourly_precipitation[i], "relative_humidity_2m" : hourly_relative_humidity_2m[i], "wind_direction_10m" : hourly_wind_direction_10m[i], "wind_speed_10m" : hourly_wind_speed_10m[i], "wind_gusts_10m" : hourly_wind_gusts_10m[i], "cloud_cover" : hourly_cloud_cover[i], "visibility" : hourly_visibility[i], "weather_code" : hourly_weather_code[i]}


        # hourly_data["temperature_2m"] = hourly_temperature_2m
        # hourly_data["surface_pressure"] = hourly_surface_pressure
        # hourly_data["precipitation"] = hourly_precipitation
        # hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        # hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
        # hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
        # hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m
        # hourly_data["cloud_cover"] = hourly_cloud_cover
        # hourly_data["visibility"] = hourly_visibility
        # hourly_data["weather_code"] = hourly_weather_code

        # hourly_dataframe = pd.DataFrame(data = hourly_data)
        return hourly_data

# start_date = datetime.datetime.now().strftime("%Y-%m-%d")
# end_date = (datetime.datetime.now() + datetime.timedelta(days = 3)).strftime("%Y-%m-%d")
# print(get_weather_data(52.52, 13.41, start_date, end_date))
