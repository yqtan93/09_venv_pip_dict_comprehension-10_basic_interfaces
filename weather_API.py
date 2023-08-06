"""This program allows user to check if it is going to rain on a particular dat using the provided weather API.
The program would ask user for the date in YYYY-mm-dd format. The weather of next day would be checked if no date is entered."""

# import required packages

import requests
import pprint
from datetime import datetime 
from dateutil import parser
import geocoder
import json

# Access geo location of a device using geocoder
def get_ip_geolocation():
# This function returns the latitude and longitude info of a user based on the computer's IP address

    try:
        # Use the 'ip' method to get the location based on the computer's IP address
        g = geocoder.ip('me')

        if g.ok:
            # Print the details of the location
            # print("Current Location Details:")
            # print(f"Latitude: {g.lat}")
            # print(f"Longitude: {g.lng}")
            # print(f"City: {g.city}")
            # print(f"Region: {g.state}")
            # print(f"Country: {g.country}")
            return g.lat, g.lng

        else:
            print("Failed to get location information.")

    except Exception as e:
        print(f"Error: {e}")


def get_name_geolocation(location_name):
    g = geocoder.geonames(location_name, key='yeqi_93')

    if g.ok:
        latitude = g.lat
        longitude = g.lng
        return latitude, longitude
    else:
        return None, None

def is_valid_date(date_string):
    try:
        # Try parsing the date using dateutil.parser
        parsed_date = parser.parse(date_string)

        # Check if the parsed date matches the format 'YYYY-mm-dd'
        return parsed_date.strftime('%Y-%m-%d') == date_string
    except parser.ParserError:
        return False
    
def weather_request(api_url):
    try:
        response = requests.get(api_url)

        if response.ok:
            print("\nRequest successful. Loading data...")
            return response.json()
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Handle request-related exceptions (e.g., connection error, timeout)
        print(f"\nError occurred during the request: {e}")

    except requests.exceptions.HTTPError as e:
        # Handle HTTP-related exceptions (e.g., 4xx, 5xx status codes)
        print(f"\nHTTP error occurred: {e}")

    except Exception as e:
        # Handle other unexpected exceptions
        print(f"\nAn unexpected error occurred: {e}")

    return None

# Request a date from user and validate input
if __name__ == "__main__":
    date = input("Please enter a date to search (YYYY-mm-dd): ")

    if is_valid_date(date):
        date_format = "%Y-%m-%d"
        searched_date = datetime.strptime(date, date_format).date()
        # You can continue processing the date if needed
        # For example: converted_date = parser.parse(user_input)
    else:
        print("Invalid date format. Please enter a date in the format 'YYYY-mm-dd'.")


#Request location from user
# searched_location = input("Please enter the name of a location to search: ")

latitude, longitude = get_ip_geolocation()

# Use IP address for geolocation if no location entered
# if searched_location.strip() == "":
#     latitude, longitude = get_ip_geolocation()
# else:

#     latitude, longitude = get_name_geolocation(searched_location)

#     if latitude is not None and longitude is not None:
#         print(f"Latitude: {latitude}, Longitude: {longitude}")
#     else:
#         print("Location not found or geolocation service error.")

# print(f"{latitude}, {longitude}")


api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=precipitation_sum&timezone=Europe%2FLondon&start_date={searched_date}&end_date={searched_date}"
local_file = "weather_log.json"

# check if entry already on existing file. If the date is already present in the file, do not make a request to the API, instead, return the result from the file.
try:
    with open(local_file, "r") as f:
        data = json.load(f)

        if data.get(date) is not None:
            req = data.get(date)
        else:
            api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=precipitation_sum&timezone=Europe%2FLondon&start_date={searched_date}&end_date={searched_date}"
            req = weather_request(api_url)
            data[date] = req
except FileNotFoundError:
    print(f"No local record file not found on system. Creating new database and request data from API...")
    data = {}
    req = weather_request(api_url)
    data[date] = req


rain_volume = req['daily']['precipitation_sum'][0]

if rain_volume == 0.0:
    print("\nIt will not rain.")
elif rain_volume >= 0.0:
    print(f"\nIt will rain. Precipitation volume: {rain_volume}")
else:
    print("I don't know.")

# Save the query results to a file. 
try:
    with open(local_file, "w") as f:
        data = json.dump(data, f)
except Exception as e:
    print(f"An error occurred while writing to the file: {e}")
else:
    print(f"Data successfully written to {local_file}")
