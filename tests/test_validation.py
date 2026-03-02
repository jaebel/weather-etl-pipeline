import unittest
import sys
import os

# Getting the absolute path to src directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')

# Add to path
sys.path.insert(0, src_dir)

# Import from validate_data.py
from validate_data import validate_weather_record, validate_temperature, validate_percentage, validate_date_format

class TestValidation(unittest.TestCase):
    
    def test_valid_record(self):
        """Test that valid data passes (concerning validated fields)"""
        data = {
            'datetime': '2026-03-01',
            'temp': 20.0,
            'max_temp': 30.0,
            'min_temp': 10.0,
            'app_max_temp': 25.0,
            'app_min_temp': 9.0,
            'high_temp': 28.0,
            'low_temp': 12.0,
            'dewpt': 5.0,
            'rh': 50,
            'pop': 50,
            'wind_dir': 50,
            'wind_spd': 10,
            'wind_gust_spd': 15,
            'pres': 1000,
            'slp': 1000,
            'uv': 5
        }
        is_valid, warnings = validate_weather_record(data)
        self.assertTrue(is_valid)
        self.assertEqual(len(warnings), 0)
    
    def test_missing_date(self):
        """Test that missing date fails validation"""
        data = {'temp': 15.5}
        is_valid, warnings = validate_weather_record(data)
        self.assertFalse(is_valid)
        self.assertIn("Missing date", warnings[0])
    
    def test_invalid_date_format(self):
        """Test that wrong date formats trigger warnings"""
        invalid_formats = [
            '25-03-2026',   # UK format
            '03-25-2026',   # US format  
            '2026/03/20',   # Slashes
            'March 20 2026' # Text
        ]

        for date_str in invalid_formats:
            data = {'datetime': date_str}
            is_valid, warnings = validate_weather_record(data)
            self.assertTrue(is_valid)
            self.assertTrue(
                any('Invalid date format' in w for w in warnings),
                f"There is no warning for date format: {date_str}"
            )
    
    def test_invalid_humidity(self):
        """Test that humidity out of range (0-100) triggers warning"""
        invalid_percents = [
            101,   # Too high
            -1,    # Negative
            500    # Way too high
        ]
        
        for percent in invalid_percents:
            data = {
                'datetime': '2026-03-20',
                'rh': percent
            }
            is_valid, warnings = validate_weather_record(data)
            self.assertTrue(is_valid)
            self.assertTrue(
                any('humidity' in w.lower() for w in warnings),
                f"There is no warning for humidity: {percent}%"
            )
    
    def test_invalid_wind_direction(self):
        """Test that wind direction out of range (0-360) triggers warning"""
        invalid_degrees = [
            366,   # Too high
            -1,    # Negative
            500    # Way too high
        ]

        for degree in invalid_degrees:
            data = {
                'datetime': '2026-03-20',
                'wind_dir': degree
            }
            is_valid, warnings = validate_weather_record(data)
            self.assertTrue(is_valid)
            self.assertTrue(
                any('wind direction' in w.lower() for w in warnings),
                f"There is no warning for wind direction: {degree}°"
            )
    
    def test_invalid_pressure(self):
        """Test that pressure out of range (800-1100 hPa) triggers warning"""
        invalid_pressures = [
            1500,  # Too high
            700,   # Too low
            -100   # Way too low
        ]

        for pressure in invalid_pressures:
            data = {
                'datetime': '2026-03-20',
                'pres': pressure
            }
            is_valid, warnings = validate_weather_record(data)
            self.assertTrue(is_valid)
            self.assertTrue(
                any('pressure' in w.lower() for w in warnings),
                f"There is no warning for pressure: {pressure} hPa"
            )
    
    def test_invalid_sea_level_pressure(self):
        """Test that sea level pressure out of range (800-1100 hPa) triggers warning"""
        invalid_pressures = [
            1500,  # Too high
            700,   # Too low
            -100   # Way too low
        ]

        for slp in invalid_pressures:
            data = {
                'datetime': '2026-03-20',
                'slp': slp
            }
            is_valid, warnings = validate_weather_record(data)
            self.assertTrue(is_valid)
            self.assertTrue(
                any('sea level pressure' in w.lower() for w in warnings),
                f"There is no warning for sea level pressure: {slp} hPa"
            )
    
    def test_invalid_uv_index(self):
        """Test that UV index out of range (0-15) triggers warning"""
        invalid_uv_values = [
            20,    # Too high
            -1,    # Negative
            100    # Way too high
        ]
    
        for uv in invalid_uv_values:
            data = {
                'datetime': '2026-02-20',
                'uv': uv
            }
            is_valid, warnings = validate_weather_record(data)
            self.assertTrue(is_valid)
            self.assertTrue(
                any('uv' in w.lower() for w in warnings),
                f"There is no warning for UV index: {uv}"
            )
    
    def test_max_less_than_min_temp(self):
        """Test that max_temp < min_temp triggers warning"""
        data = {
            'datetime': '2026-02-20',
            'max_temp': 10,
            'min_temp': 20
        }
        is_valid, warnings = validate_weather_record(data)
        self.assertTrue(is_valid)
        self.assertTrue(
            any('max_temp' in w and 'min_temp' in w for w in warnings),
            "There is no warning for max_temp < min_temp"
        )
    
    def test_wind_gust_less_than_wind_speed(self):
        """Test that wind_gust < wind_spd triggers warning"""
        data = {
            'datetime': '2026-02-20',
            'wind_spd': 20,
            'wind_gust_spd': 10
        }
        is_valid, warnings = validate_weather_record(data)
        self.assertTrue(is_valid)
        self.assertTrue(
            any('gust' in w.lower() and 'wind' in w.lower() for w in warnings),
            "There is no warning for wind_gust < wind_spd"
        )
    
    def test_negative_wind_speed(self):
        """Test that negative wind speed triggers warning"""
        data = {
            'datetime': '2026-02-20',
            'wind_spd': -5
        }
        is_valid, warnings = validate_weather_record(data)
        self.assertTrue(is_valid)
        self.assertTrue(
            any('negative' in w.lower() or 'wind' in w.lower() for w in warnings),
            "There is no warning for negative wind speed"
        )

    # Testing specific validation functions
    
    def test_temperature_range(self):
        """Test temperature validation function"""
        self.assertTrue(validate_temperature(20))
        self.assertTrue(validate_temperature(-50))
        self.assertTrue(validate_temperature(None))
        self.assertFalse(validate_temperature(150))
        self.assertFalse(validate_temperature(-200))
    
    def test_percentage_range(self):
        """Test percentage validation function"""
        self.assertTrue(validate_percentage(50))
        self.assertTrue(validate_percentage(0))
        self.assertTrue(validate_percentage(100))
        self.assertTrue(validate_percentage(None))
        self.assertFalse(validate_percentage(101))
        self.assertFalse(validate_percentage(-1))
    
    def test_date_format_validation(self):
        """Test date format validation function"""
        self.assertTrue(validate_date_format('2026-02-20'))
        self.assertTrue(validate_date_format('2024-12-31'))
        self.assertFalse(validate_date_format('20/02/2026'))
        self.assertFalse(validate_date_format('2026-13-01'))
        self.assertFalse(validate_date_format('not-a-date'))
        self.assertFalse(validate_date_format(None))
        self.assertFalse(validate_date_format(''))

if __name__ == '__main__':
    unittest.main()