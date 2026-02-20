import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_tables():
    """Create the database tables for weather data"""
    
    # Connection params from environment variables
    conn_params = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        print("Connected to database successfully!")
        
        # Create cities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cities (
                city_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                country_code VARCHAR(10),
                state_code VARCHAR(50),
                latitude DECIMAL(10, 7) NOT NULL,
                longitude DECIMAL(10, 7) NOT NULL,
                timezone VARCHAR(50),
                UNIQUE(latitude, longitude)
            );
        """)
        print("Created 'cities' table")
        
        # Create daily_weather table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_weather (
                id SERIAL PRIMARY KEY,
                city_id INTEGER NOT NULL REFERENCES cities(city_id) ON DELETE CASCADE,
                forecast_date DATE NOT NULL,
                
                -- Temperature fields
                temp DECIMAL(5, 2),
                max_temp DECIMAL(5, 2),
                min_temp DECIMAL(5, 2),
                apparent_max_temp DECIMAL(5, 2),
                apparent_min_temp DECIMAL(5, 2),
                high_temp DECIMAL(5, 2),
                low_temp DECIMAL(5, 2),
                dewpt DECIMAL(5, 2),
                
                -- Precipitation
                precipitation DECIMAL(7, 4),
                pop INTEGER,
                snow DECIMAL(7, 4),
                snow_depth DECIMAL(7, 4),
                
                -- Wind
                wind_speed DECIMAL(5, 2),
                wind_gust_spd DECIMAL(5, 2),
                wind_dir INTEGER,
                wind_cdir VARCHAR(10),
                wind_cdir_full VARCHAR(50),
                
                -- Clouds and visibility
                clouds INTEGER,
                clouds_hi INTEGER,
                clouds_low INTEGER,
                clouds_mid INTEGER,
                vis DECIMAL(5, 2),
                
                -- Atmospheric
                humidity INTEGER,
                pressure DECIMAL(7, 2),
                slp DECIMAL(7, 2),
                ozone DECIMAL(7, 2),
                uv DECIMAL(3, 1),
                
                -- Weather description
                weather_code INTEGER,
                weather_description VARCHAR(100),
                weather_icon VARCHAR(10),
                
                -- Moon/sun
                moon_phase DECIMAL(4, 2),
                moon_phase_lunation DECIMAL(4, 2),
                sunrise_ts BIGINT,
                sunset_ts BIGINT,
                moonrise_ts BIGINT,
                moonset_ts BIGINT,
                       
                -- Solar radiation
                max_dhi DECIMAL(7, 4),
                
                -- Metadata
                ts BIGINT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(city_id, forecast_date)
            );
        """)
        print("Created 'daily_weather' table")
        
        # Commit changes
        conn.commit()
        print("\nDatabase schema created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    create_tables()