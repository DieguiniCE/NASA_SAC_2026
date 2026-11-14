"""Configuration constants for the AgroClima Costa Rica application."""

# Application branding
APP_TITLE = "AgroClima CR | NASA Space Apps"
APP_SUBTITLE = "Costa Rica Agro-Climatic Crop Suitability Explorer"
APP_ICON = "🌱"

# Costa Rica Geographical Boundaries
COSTA_RICA_CENTER = [9.7489, -83.7534]
DEFAULT_ZOOM = 8

CR_LAT_MIN = 8.0
CR_LAT_MAX = 11.3
CR_LON_MIN = -86.0
CR_LON_MAX = -82.5

# NASA POWER API Configurations
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
NASA_POWER_COMMUNITY = "AG"  # Agroclimatology Community

# Key agroclimatological parameters from NASA POWER
NASA_PARAMETERS = [
    "T2M",               # Temperature at 2 Meters (°C)
    "T2M_MAX",           # Maximum Temperature at 2 Meters (°C)
    "T2M_MIN",           # Minimum Temperature at 2 Meters (°C)
    "PRECTOTCORR",       # Precipitation Corrected (mm/day)
    "RH2M",              # Relative Humidity at 2 Meters (%)
    "ALLSKY_SFC_SW_DWN", # Solar Irradiance (MJ/m^2/day or kW-hr/m^2/day)
    "WS2M",              # Wind Speed at 2 Meters (m/s)
]

# Month labels
MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
