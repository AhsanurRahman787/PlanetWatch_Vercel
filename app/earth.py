import requests

def is_ocean(lat, lon):
    try:
        mask = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode&forecast_days=1",
            timeout=2
        ).json()["daily"]["land_sea_mask"][0]
        return mask == 0
    except:
        return False