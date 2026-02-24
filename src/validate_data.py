import re
from datetime import datetime

def validate_date_format(date_str):
    """
    Validate date is in YYYY-MM-DD format
    """
    if not date_str:
        return False
    
    # Check format with regex
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False
    
    # Verify it's a real date
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_temperature(temp, min_temp=-150, max_temp=100):
    if temp is None:
        return True  # Allow nulls
    
    try:
        temp_float = float(temp)
        return min_temp <= temp_float <= max_temp
    except (ValueError, TypeError):
        return False

def validate_percentage(value):
    if value is None:
        return True  # Allow nulls
    
    try:
        value_float = float(value)
        return 0 <= value_float <= 100
    except (ValueError, TypeError):
        return False

def validate_weather_record(day_data):
    """
    Validate a single day's data
    Allow partial records but reject if date is missing
    
    Returns: tuple: (is_valid, warnings_list)
    """
    warnings = []
    
    # CRITICAL: Date must exist
    date = day_data.get('datetime')
    if not date:
        return False, ["Missing date - cannot insert record"]
    
    # Validate date format
    if not validate_date_format(date):
        warnings.append(f"Invalid date format: {date}")
    
    # Validate temperature fields
    temp_fields = {
        'temp': day_data.get('temp'),
        'max_temp': day_data.get('max_temp'),
        'min_temp': day_data.get('min_temp'),
        'app_max_temp': day_data.get('app_max_temp'),
        'app_min_temp': day_data.get('app_min_temp'),
        'high_temp': day_data.get('high_temp'),
        'low_temp': day_data.get('low_temp'),
        'dewpt': day_data.get('dewpt')
    }
    
    for field_name, value in temp_fields.items():
        if value is not None and not validate_temperature(value):
            warnings.append(f"Temperature out of range: {field_name}={value}°C")
    
    # Validate percentages
    humidity = day_data.get('rh')
    if humidity is not None and not validate_percentage(humidity):
        warnings.append(f"Invalid humidity: {humidity}% (must be 0-100)")
    
    pop = day_data.get('pop')
    if pop is not None and not validate_percentage(pop):
        warnings.append(f"Invalid precipitation probability: {pop}% (must be 0-100)")
    
    # Validate wind direction (0-360 degrees)
    wind_dir = day_data.get('wind_dir')
    if wind_dir is not None and not (0 <= wind_dir <= 360):
        warnings.append(f"Invalid wind direction: {wind_dir}° (must be 0-360)")
    
    # Validate pressure (800-1100 hPa)
    pres = day_data.get('pres')
    if pres is not None and not (800 <= pres <= 1100):
        warnings.append(f"Invalid pressure: {pres} hPa (must be 800-1100)")
    
    slp = day_data.get('slp')
    if slp is not None and not (800 <= slp <= 1100):
        warnings.append(f"Invalid sea level pressure: {slp} hPa (must be 800-1100)")
    
    # Validate UV (0-15)
    uv = day_data.get('uv')
    if uv is not None and not (0 <= uv <= 15):
        warnings.append(f"Invalid UV index: {uv} (must be 0-15)")
    
    # Check logical consistency: max_temp >= min_temp
    max_temp = day_data.get('max_temp')
    min_temp = day_data.get('min_temp')
    if max_temp is not None and min_temp is not None:
        if max_temp < min_temp:
            warnings.append(f"max_temp ({max_temp}) < min_temp ({min_temp})")
    
    # Validate wind speed (non-negative)
    wind_spd = day_data.get('wind_spd')
    if wind_spd is not None and wind_spd < 0:
        warnings.append(f"Negative wind speed: {wind_spd}")
    
    # Validate wind gust >= wind speed
    wind_gust_spd = day_data.get('wind_gust_spd')
    if wind_gust_spd is not None and wind_spd is not None:
        if wind_gust_spd < wind_spd:
            warnings.append(f"Wind gust ({wind_gust_spd}) < wind speed ({wind_spd})")
    
    # Record is valid if date exists - warnings are extra details
    return True, warnings

def log_validation_results(city_name, forecast_date, warnings):
    if warnings:
        print(f"Data quality warnings for {city_name} on {forecast_date}:")
        for warning in warnings:
            print(f"  - {warning}")