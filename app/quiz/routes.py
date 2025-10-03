from flask import render_template, jsonify
from app.quiz import bp
import requests
from datetime import datetime, timedelta

# YOUR NASA API KEY - HARDCODED DIRECTLY
NASA_API_KEY = "i4qSfG0QQG1E05NrJ8NEr3RyMkmAD7dB83edeElz"

# NASA API endpoints
NEO_BROWSE = "https://api.nasa.gov/neo/rest/v1/neo/browse?page=0&size=10"

# Simulated Impacter 25 asteroid
IMPACTER_25 = {
    "id": "impacter-25",
    "name": "Impacter 25",
    "absolute_magnitude_h": 22.5,
    "estimated_diameter": {
        "kilometers": {
            "estimated_diameter_min": 0.110,
            "estimated_diameter_max": 0.246
        }
    },
    "is_potentially_hazardous_asteroid": True,
    "close_approach_data": [
        {
            "close_approach_date": "2023-10-15",
            "relative_velocity": {
                "kilometers_per_second": "12.5"
            },
            "miss_distance": {
                "kilometers": "0.01"
            }
        }
    ],
    "orbital_data": {
        "orbit_class": {
            "orbit_class_type": "Apollo"
        },
        "semi_major_axis": "1.2",
        "eccentricity": "0.4",
        "inclination": "5.2",
        "perihelion_distance": "0.8",
        "aphelion_distance": "1.6"
    }
}

@bp.route('/')
def solar_system():
    return render_template('part2.html')

@bp.route('/part2')
def solar():
    return render_template('quiz.html')

@bp.route('/page3')
def solar2():
    return render_template('page3.html')

@bp.route('/api/asteroids')
def get_asteroids():
    try:
        params = {'api_key': NASA_API_KEY}  # Using hardcoded key
        response = requests.get(NEO_BROWSE, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        asteroids = data.get('near_earth_objects', [])
        asteroids.append(IMPACTER_25)
        return jsonify(asteroids)
    except Exception as e:
        return jsonify([IMPACTER_25])

 