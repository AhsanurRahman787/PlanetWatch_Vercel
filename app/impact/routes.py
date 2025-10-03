from flask import Blueprint, render_template, request, jsonify
from app.config import Config
from app.physics import overpressure, wind_ms, thermal, crater, seismic 
from app.earth import is_ocean
from app.story import generate_zone_story
import random
from app.impact import bp  # This is the main blueprint

def get_terrain_height(lat, lon):
    """Get elevation data (mock for faster loading)"""
    return random.uniform(0, 3000)

def generate_elevation_map(lat, lon, radius_km):
    """Generate elevation grid (mock for faster loading)"""
    grid = []
    step = max(0.01, radius_km / 10)
    for lat_offset in range(-int(radius_km), int(radius_km) + 1):
        row = []
        for lon_offset in range(-int(radius_km), int(radius_km) + 1):
            distance = (lat_offset**2 + lon_offset**2)**0.5
            base_elevation = random.uniform(0, 1000)
            if distance < radius_km / 2:
                base_elevation *= (1 - distance / (radius_km / 2))
            row.append(base_elevation)
        grid.append(row)
    return grid

@bp.route("/")
def impact_page():
    return render_template("impact.html")

@bp.route("/impact2")
def impact():
    return render_template("impact2.html")

@bp.route("/sim", methods=["POST"])
def sim():
    data = request.json
    lat = float(data["lat"])
    lon = float(data["lon"])
    dist = float(data["dist"])
    en = float(data["en"])
    ang = float(data.get("angle", 45))
    
    E = en * 4.184e15
    c = crater(E)
    s = seismic(E, dist)
    op = overpressure(E, dist)
    w = wind_ms(op)
    th = thermal(E, dist)
    ocean = is_ocean(lat, lon)
    ts = 0.14 * c * 1000 if ocean else 0

    # Generate zone stories
    texts = {
        "crater": generate_zone_story("crater", c, s, op, w, th, ts),
        "shock": generate_zone_story("shock", c, s, op, w, th, ts),
        "quake": generate_zone_story("quake", c, s, op, w, th, ts),
        "tsunami": generate_zone_story("tsunami", c, s, op, w, th, ts) if ocean else "No tsunami risk."
    }

    return jsonify({
        "crater": round(c, 1),
        "seismic": round(s, 1),
        "wind": int(w),
        "thermal": int(th),
        "tsunami": round(ts, 1),
        "angle": ang,
        "texts": texts,
        "terrain_height": get_terrain_height(lat, lon),
        "elevation_map": generate_elevation_map(lat, lon, max(c, s, ts))
    })