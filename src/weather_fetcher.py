import pandas as pd
from meteostat import Point, Daily
from datetime import datetime, date
import time
import os
import ssl
import certifi

# Fix SSL certificate issue
ssl._create_default_https_context = ssl._create_unverified_context

def fetch_weather_data(start_date, end_date, lat, lon):
    """Fetch historical weather data using Meteostat"""
    try:
        # Create Point for Istanbul
        location = Point(lat, lon)
        
        # Convert dates to datetime
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        elif isinstance(start_date, date):
            start_date = datetime.combine(start_date, datetime.min.time())
            
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        elif isinstance(end_date, date):
            end_date = datetime.combine(end_date, datetime.min.time())
        
        print(f"Fetching data for date range: {start_date} to {end_date}")
        
        # Get daily weather data
        data = Daily(location, start_date, end_date)
        data = data.fetch()
        
        # Reset index to make date a column
        data = data.reset_index()
        
        # Rename columns for clarity
        data = data.rename(columns={
            'date': 'date',
            'tavg': 'temp_mean',
            'tmin': 'temp_min',
            'tmax': 'temp_max',
            'prcp': 'precipitation',
            'snow': 'snow',
            'wdir': 'wind_direction',
            'wspd': 'wind_speed',
            'wpgt': 'wind_gust',
            'pres': 'pressure',
            'tsun': 'sunshine_hours'
        })
        
        return data
        
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        print(f"Start date type: {type(start_date)}")
        print(f"End date type: {type(end_date)}")
        return None

def main():
    # Read step data
    step_data = pd.read_csv('data/step_data.csv')
    
    # Convert dates to datetime
    step_data['start_date'] = pd.to_datetime(step_data['start_date'])
    
    # Get date range
    start_date = step_data['start_date'].min().to_pydatetime()
    end_date = step_data['start_date'].max().to_pydatetime()
    
    print(f"Fetching weather data from {start_date.date()} to {end_date.date()}...")
    
    # Istanbul coordinates
    CITY_LAT = 41.0082
    CITY_LON = 28.9784
    
    # Fetch weather data
    weather_df = fetch_weather_data(start_date, end_date, CITY_LAT, CITY_LON)
    
    if weather_df is not None:
        # Fill missing values with forward fill and then backward fill
        weather_df = weather_df.fillna(method='ffill').fillna(method='bfill')
        
        output_file = 'data/weather_data.csv'
        
        # Save to CSV
        weather_df.to_csv(output_file, index=False)
        print(f"\nWeather data saved to {output_file}")
        print(f"Successfully retrieved weather data for {len(weather_df)} days")
        
        # Print sample of the data
        print("\nSample of weather data:")
        print(weather_df.head())
        
        # Print data info
        print("\nWeather data information:")
        print(weather_df.info())
    else:
        print("No weather data was retrieved")

if __name__ == "__main__":
    main() 