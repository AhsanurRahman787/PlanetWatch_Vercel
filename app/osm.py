import requests
from typing import List, Dict


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def fetch_osm_shelters(lat: float, lon: float, radius_km: int = 20) -> List[Dict[str, float]]:
    """
    Query Overpass for shelter-like objects inside radius_km kilometres.
    """
    radius_m = int(radius_km * 1000)

    # Overpass QL: nodes, ways and relations tagged as shelters
    query = f"""
    [out:json][timeout:30];
    (
      node["emergency"="shelter"](around:{radius_m},{lat},{lon});
      node["amenity"="shelter"](around:{radius_m},{lat},{lon});
      node["shelter"="yes"](around:{radius_m},{lat},{lon});
      way["emergency"="shelter"](around:{radius_m},{lat},{lon});
      relation["emergency"="shelter"](around:{radius_m},{lat},{lon});
    );
    out center;
    """

    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            timeout=35
        )
        response.raise_for_status()
    except requests.RequestException:
        # Logged by caller if needed; fail silently for user
        return []

    elements = response.json().get("elements", [])
    shelters: List[Dict[str, float]] = []

    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("ref") or "Unnamed shelter"

        if el["type"] == "node":
            lat_el, lon_el = el["lat"], el["lon"]
        else:  # way or relation
            center = el.get("center")
            if not center:
                continue
            lat_el, lon_el = center["lat"], center["lon"]

        shelters.append({"name": name, "lat": lat_el, "lon": lon_el})

    return shelters