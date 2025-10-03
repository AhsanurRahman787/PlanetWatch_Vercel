import math
from app.config import Config as C

def overpressure(E_J, r_km):
    """
    Returns overpressure (Pa) at a distance r_km from an impact with energy E_J (Joules)
    Caps at plausible maximum values.
    """
    # Prevent division by zero / extremely small distances
    r_m = max(r_km * 1000, 100)  # minimum 100 m
    # Scaling formula based on empirical impact models
    p = 75000 * (290 / r_m) ** 1.3 * ((E_J / C.K_t) ** (1 / 3))
    # Cap at 5 MPa (~plausible maximum near ground zero)
    return max(0, min(p, 5e6))

def wind_ms(Pa):
    """
    Convert overpressure (Pa) to wind speed (m/s) using dynamic pressure approximation:
    P = 0.5 * rho * v^2
    """
    v = math.sqrt(max(Pa, 0) / C.PO)
    # Cap wind at ~200 m/s (hypersonic winds are unrealistic)
    return min(v, 200)

def thermal(E_J, r_km):
    """
    Thermal radiation flux (J/m²) at distance r_km
    Assumes ~1% of impact energy radiated as heat
    """
    r_m = max(r_km * 1000, 100)  # minimum 100 m
    flux = 0.01 * E_J / (4 * math.pi * r_m ** 2)
    # Cap thermal flux to ~10 MJ/m² (plausible maximum)
    return min(flux, 1e7)

def crater(E_J):
    """
    Crater diameter (km) from impact energy (Joules)
    Cube-root scaling: D ~ 1 km * (E in Mt)^(1/3)
    """
    E_Mt = E_J / 4.184e15  # Joules → Mt TNT
    return 1.0 * E_Mt ** (1 / 3)

def seismic(E_J, r_km):
    """
    Richter magnitude at distance r_km from an impact of energy E_J
    Uses empirical scaling with attenuation
    """
    M0 = 0.67 * math.log10(E_J) - 5.87  # base magnitude from energy
    if r_km <= 0:
        return M0 + 1.0  # boost for ground zero
    # Attenuation with distance
    if r_km < 60:
        att = 0.0238 * r_km
    elif r_km < 700:
        att = 0.0048 * r_km - 1.1644
    else:
        att = 1.66 * math.log10(r_km) - 6.399
    return max(M0 - att, 0)  # magnitude cannot be negative
