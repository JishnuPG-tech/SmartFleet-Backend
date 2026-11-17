import math
from typing import Tuple, Optional

# Kerala NH-66 Reference Waypoints for Fleet Geofencing & Simulation
KERALA_HUBS = {
    "KAS": {"name": "Kasaragod Hub", "lat": 12.5102, "lng": 74.9852},
    "CAN": {"name": "Kannur Hub", "lat": 11.8745, "lng": 75.3704},
    "CCJ": {"name": "Kozhikode Hub", "lat": 11.2588, "lng": 75.7804},
    "TCR": {"name": "Thrissur Hub", "lat": 10.5276, "lng": 76.2144},
    "COK": {"name": "Kochi Port", "lat": 9.9312, "lng": 76.2673},
    "ALP": {"name": "Alappuzha Hub", "lat": 9.4981, "lng": 76.3388},
    "QLN": {"name": "Kollam Port", "lat": 8.8932, "lng": 76.6141},
    "TRV": {"name": "Thiruvananthapuram Central", "lat": 8.5241, "lng": 76.9366},
}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth in kilometers.
    Uses the Haversine formula.
    """
    R = 6371.0 # Earth radius in kilometers

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def calculate_heading(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate forward azimuth / compass heading from (lat1, lon1) to (lat2, lon2).
    Returns degrees in [0, 360).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    bearing = math.degrees(math.atan2(y, x))
    return round((bearing + 360.0) % 360.0, 1)

def interpolate_position(
    lat1: float, lon1: float, lat2: float, lon2: float, fraction: float
) -> Tuple[float, float]:
    """
    Interpolate coordinate between point 1 and point 2 by fraction [0.0, 1.0].
    """
    fraction = max(0.0, min(1.0, fraction))
    lat = lat1 + (lat2 - lat1) * fraction
    lon = lon1 + (lon2 - lon1) * fraction
    return round(lat, 6), round(lon, 6)

def estimate_eta_minutes(distance_km: float, speed_kmh: float = 40.0) -> int:
    """
    Estimate remaining travel time in minutes based on average NH-66 commercial speed (40 km/h).
    """
    if speed_kmh <= 0:
        speed_kmh = 40.0
    hours = distance_km / speed_kmh
    return max(1, int(round(hours * 60)))
