# import required packages
import requests
import pprint
from datetime import datetime, timedelta 
from dateutil import parser
import geocoder
import json


# exception classes
class InvalidDate(Exception):
    def __init__(self):
        self.message = "\nInvalid date format. Please enter a date in the format 'YYYY-mm-dd'."
        super().__init__(self.message)

# creating weather forecast class
class WeatherForecast:

    history = {}
    
    def __init__(self, date, city = ""): 
        self.index = 0
        self.date = date
        self.city = self.set_location(city)
        # Load data if history is empty
        if not type(self).history:
            self.load_history()       
        
    # to validate date input
    def _check_date(self, date):
        try:
            # Try parsing the date using dateutil.parser
            parsed_date = parser.parse(date)
            # Check if the parsed date matches the format 'YYYY-mm-dd'
            return parsed_date.strftime('%Y-%m-%d') == date
        except parser.ParserError:
            return False
        
    def set_date(self):
    # define validated date value, use tomorrows date if empty value
        if self._check_date(self.date):
            date_format = "%Y-%m-%d"
            date = datetime.strptime(self.date, date_format).date()
            return date
        elif self.date.strip() == "":
            today = datetime.now().date()
            date = today + timedelta(days=1)
            return date
        else:
            raise InvalidDate()

    def get_name_geolocation(self, city):
        g = geocoder.osm(city)

        if g.ok:
            self.latitude = g.x
            self.longitude = g.y
            return self.latitude, self.longitude
        else:
            return None, None
        
    def get_ip_geolocation(self):
        try:
            # Use the 'ip' method to get the location based on the computer's IP address
            g = geocoder.ip('me')

            if g.ok:
                return g.lat, g.lng, g.city

            else:
                print("\nFailed to get location information.")

        except Exception as e:
            print(f"Error: {e}")

    def set_location(self, city):
        # Define location, use IP location if no city entered or error finding location
        if city.strip() == "":
            self.latitude, self.longitude, self.city = self.get_ip_geolocation()
            return self.latitude, self.longitude, self.city

        elif self.latitude is None and self.longitude is None:
            print("\nLocation not found or geolocation service error. Using current IP location...")
            self.latitude, self.longitude, self.city = self.get_ip_geolocation()
            return self.latitude, self.longitude, self.city

        else:
            self.latitude, self.longitude = self.get_name_geolocation(city)
            return self.latitude, self.longitude

    def load_history(self, file='weather_log.json'): 
        # Load history from file
        try:
            with open(file, "r") as f:
                type(self).history = json.load(f)

        except FileNotFoundError:
            print(f"Local record file not found on system. Creating new database...")
    
    def save_history(self, file='weather_log.json'):
        try:
            with open(file, "w") as f:
                json.dump(type(self).history, f)
        except Exception as e:
                print(f"An error occurred while writing to the file: {e}")
        else:
                print(f"Data successfully written to {file}")
        
    def __setitem__(self): # set weather forecast for a particular date
        self[self.date] = self.forecast

    def __getitem__(self): # get weather forecast for particular date
            type(self).history[self.date]

    def get_forecast(self):
        if self.date in type(self).history:
            type(self).history[self.date]
        else:
        # retrieve data via API request
            req = self.weather_request()
            rain_volume = req['daily']['precipitation_sum'][0]

            if rain_volume == 0.0:
                forecast = "It will not rain."
            elif rain_volume >= 0.0:
                forecast = f"It will rain. Precipitation volume: {rain_volume}"
            else:
                forecast = "I don't know."

        # save data to history
            type(self).history[self.date] = forecast
            self.save_history()


    def weather_request(self):
        date = self.set_date()
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={self.latitude}&longitude={self.longitude}&daily=precipitation_sum&timezone=Europe%2FLondon&start_date={self.date}&end_date={self.date}"
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

    def __iter__(self): #iterate over all the dates for which weather forecast is known
        return self
    
    def __next__(self):
        if self.index < len(self.keys):
            key = self.keys[self.index]
            self.index += 1
            return key
        raise StopIteration

        
    def items(self): # return a generator of tuples in the format of (date, weather)
        for date, weather in type(self).history.items():
            yield date, weather


if __name__ == "__main__":
    date = input("Please enter a date to search (YYYY-mm-dd): ")
    searched_location = input("Please enter the name of a location to search: ")

    weather_forecast = WeatherForecast(date, searched_location)

    weather_forecast.get_forecast()
     