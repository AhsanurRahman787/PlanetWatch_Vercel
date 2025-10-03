import folium
from app.geo02 import haversine
from pathlib import Path

def create_map(
    user_lat: float,
    user_lon: float,
    shelters: list[dict],
) -> str:

    # Base map centered on user location
    m = folium.Map(location=[user_lat, user_lon], zoom_start=12)

    # User location marker
    folium.Marker(
        [user_lat, user_lon],
        popup="Your Location",
        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
    ).add_to(m)

    # Shelter markers
    for s in shelters:
        dist = haversine(user_lat, user_lon, s["lat"], s["lon"])
        color = "green"
        icon = "home"
        folium.Marker(
            [s["lat"], s["lon"]],
            popup=f"{s['name']} ({dist:.1f} km away)",
            icon=folium.Icon(color=color, icon=icon, prefix="fa"),
        ).add_to(m)

    return m._repr_html_()  # Return HTML for iframe
