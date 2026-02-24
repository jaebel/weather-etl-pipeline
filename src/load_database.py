import psycopg2
import os
from dotenv import load_dotenv
from extract import fetch_weather_data, load_config
from validate_data import validate_weather_record, log_validation_results

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create and return a database connection"""
    conn_params = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }
    return psycopg2.connect(**conn_params)

def insert_or_get_city(cursor, city_data, api_response):
    """
    Insert city if it doesn't exist, or get existing city_id
    Returns city_id - an integer primary key
    """
    # Extract data from API response, or config.yaml/ city_data as backup
    city_name = api_response.get('city_name', city_data['name'])
    country_code = api_response.get('country_code')
    state_code = api_response.get('state_code')
    latitude = api_response.get('lat', city_data['lat'])
    longitude = api_response.get('lon', city_data['lon'])
    timezone = api_response.get('timezone')
    
    # Check if city already exists (by lat/lon)
    cursor.execute("""
        SELECT city_id FROM cities 
        WHERE latitude = %s AND longitude = %s
    """, (latitude, longitude))
    
    result = cursor.fetchone()
    
    if result:
        # City exists, return the ID
        return result[0]
    else:
        # City doesn't exist, insert it
        cursor.execute("""
            INSERT INTO cities (name, country_code, state_code, latitude, longitude, timezone)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING city_id
        """, (city_name, country_code, state_code, latitude, longitude, timezone))
        
        return cursor.fetchone()[0]

def transform_weather_record(day_data):
    """
    Transform API weather data to match database schema
    Returns a dictionary with keys matching database columns
    """
    # Extract nested weather object
    weather = day_data.get('weather', {})
    
    return {
        'forecast_date': day_data.get('datetime'),
        'temp': day_data.get('temp'),
        'max_temp': day_data.get('max_temp'),
        'min_temp': day_data.get('min_temp'),
        'apparent_max_temp': day_data.get('app_max_temp'),
        'apparent_min_temp': day_data.get('app_min_temp'),
        'high_temp': day_data.get('high_temp'),
        'low_temp': day_data.get('low_temp'),
        'dewpt': day_data.get('dewpt'),
        'precipitation': day_data.get('precip'),
        'pop': day_data.get('pop'),
        'snow': day_data.get('snow'),
        'snow_depth': day_data.get('snow_depth'),
        'wind_speed': day_data.get('wind_spd'),
        'wind_gust_spd': day_data.get('wind_gust_spd'),
        'wind_dir': day_data.get('wind_dir'),
        'wind_cdir': day_data.get('wind_cdir'),
        'wind_cdir_full': day_data.get('wind_cdir_full'),
        'clouds': day_data.get('clouds'),
        'clouds_hi': day_data.get('clouds_hi'),
        'clouds_low': day_data.get('clouds_low'),
        'clouds_mid': day_data.get('clouds_mid'),
        'vis': day_data.get('vis'),
        'humidity': day_data.get('rh'),
        'pressure': day_data.get('pres'),
        'slp': day_data.get('slp'),
        'ozone': day_data.get('ozone'),
        'uv': day_data.get('uv'),
        'weather_code': weather.get('code'),
        'weather_description': weather.get('description'),
        'weather_icon': weather.get('icon'),
        'moon_phase': day_data.get('moon_phase'),
        'moon_phase_lunation': day_data.get('moon_phase_lunation'),
        'sunrise_ts': day_data.get('sunrise_ts'),
        'sunset_ts': day_data.get('sunset_ts'),
        'moonrise_ts': day_data.get('moonrise_ts'),
        'moonset_ts': day_data.get('moonset_ts'),
        'max_dhi': day_data.get('max_dhi'),
        'ts': day_data.get('ts')
    }

def insert_weather_record(cursor, city_id, weather_data):
    """
    Insert a single weather record into the database
    """
    cursor.execute("""
        INSERT INTO daily_weather (
            city_id, forecast_date, temp, max_temp, min_temp,
            apparent_max_temp, apparent_min_temp, high_temp, low_temp, dewpt,
            precipitation, pop, snow, snow_depth,
            wind_speed, wind_gust_spd, wind_dir, wind_cdir, wind_cdir_full,
            clouds, clouds_hi, clouds_low, clouds_mid, vis,
            humidity, pressure, slp, ozone, uv,
            weather_code, weather_description, weather_icon,
            moon_phase, moon_phase_lunation, sunrise_ts, sunset_ts, moonrise_ts, moonset_ts,
            max_dhi, ts
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s
        )
        ON CONFLICT (city_id, forecast_date) DO UPDATE SET
            temp = EXCLUDED.temp,
            max_temp = EXCLUDED.max_temp,
            min_temp = EXCLUDED.min_temp,
            apparent_max_temp = EXCLUDED.apparent_max_temp,
            apparent_min_temp = EXCLUDED.apparent_min_temp,
            high_temp = EXCLUDED.high_temp,
            low_temp = EXCLUDED.low_temp,
            dewpt = EXCLUDED.dewpt,
            precipitation = EXCLUDED.precipitation,
            pop = EXCLUDED.pop,
            snow = EXCLUDED.snow,
            snow_depth = EXCLUDED.snow_depth,
            wind_speed = EXCLUDED.wind_speed,
            wind_gust_spd = EXCLUDED.wind_gust_spd,
            wind_dir = EXCLUDED.wind_dir,
            wind_cdir = EXCLUDED.wind_cdir,
            wind_cdir_full = EXCLUDED.wind_cdir_full,
            clouds = EXCLUDED.clouds,
            clouds_hi = EXCLUDED.clouds_hi,
            clouds_low = EXCLUDED.clouds_low,
            clouds_mid = EXCLUDED.clouds_mid,
            vis = EXCLUDED.vis,
            humidity = EXCLUDED.humidity,
            pressure = EXCLUDED.pressure,
            slp = EXCLUDED.slp,
            ozone = EXCLUDED.ozone,
            uv = EXCLUDED.uv,
            weather_code = EXCLUDED.weather_code,
            weather_description = EXCLUDED.weather_description,
            weather_icon = EXCLUDED.weather_icon,
            moon_phase = EXCLUDED.moon_phase,
            moon_phase_lunation = EXCLUDED.moon_phase_lunation,
            sunrise_ts = EXCLUDED.sunrise_ts,
            sunset_ts = EXCLUDED.sunset_ts,
            moonrise_ts = EXCLUDED.moonrise_ts,
            moonset_ts = EXCLUDED.moonset_ts,
            max_dhi = EXCLUDED.max_dhi,
            ts = EXCLUDED.ts
    """, (
        city_id,
        weather_data['forecast_date'],
        weather_data['temp'],
        weather_data['max_temp'],
        weather_data['min_temp'],
        weather_data['apparent_max_temp'],
        weather_data['apparent_min_temp'],
        weather_data['high_temp'],
        weather_data['low_temp'],
        weather_data['dewpt'],
        weather_data['precipitation'],
        weather_data['pop'],
        weather_data['snow'],
        weather_data['snow_depth'],
        weather_data['wind_speed'],
        weather_data['wind_gust_spd'],
        weather_data['wind_dir'],
        weather_data['wind_cdir'],
        weather_data['wind_cdir_full'],
        weather_data['clouds'],
        weather_data['clouds_hi'],
        weather_data['clouds_low'],
        weather_data['clouds_mid'],
        weather_data['vis'],
        weather_data['humidity'],
        weather_data['pressure'],
        weather_data['slp'],
        weather_data['ozone'],
        weather_data['uv'],
        weather_data['weather_code'],
        weather_data['weather_description'],
        weather_data['weather_icon'],
        weather_data['moon_phase'],
        weather_data['moon_phase_lunation'],
        weather_data['sunrise_ts'],
        weather_data['sunset_ts'],
        weather_data['moonrise_ts'],
        weather_data['moonset_ts'],
        weather_data['max_dhi'],
        weather_data['ts']
    ))

def main():
    """
    Run the ETL pipeline - Extract, Transform, Load
    """
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        print("Connected to database successfully!")
        
        # Load config (cities from config.yaml)
        config = load_config()
        
        # Process each city
        for city in config['cities']:
            print(f"\nProcessing {city['name']}...")
            
            # Extract: Fetch weather data from API
            api_response = fetch_weather_data(city['lat'], city['lon'])
            
            if not api_response:
                print(f"Failed to fetch data for {city['name']}")
                continue
            
            # Insert or get city
            city_id = insert_or_get_city(cursor, city, api_response)
            print(f"City ID: {city_id}")
            
            # Process each day of weather data
            weather_days = api_response.get('data', [])
            for day_data in weather_days:

                is_valid, warnings = validate_weather_record(day_data)
    
                if not is_valid:
                    print(f"Skipping record: {warnings}")
                    continue
                
                # Log warnings (but still insert)
                if warnings:
                    log_validation_results(city['name'], day_data.get('datetime'), warnings)

                # Transform: Convert API format to DB format
                transformed_data = transform_weather_record(day_data)
                
                # Load: Insert into database
                insert_weather_record(cursor, city_id, transformed_data)
            
            print(f"Loaded {len(weather_days)} days of weather data for {city['name']}")
        
        # Commit all changes
        conn.commit()
        print("\nETL pipeline completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()