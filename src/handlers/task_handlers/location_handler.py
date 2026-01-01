from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="My Application") # Replace "your_app_name" with a specific name

def get_address(latitude: float, longitude: float):
    # 1. Define the coordinates (latitude, longitude)
    coordinates = f"{latitude}, {longitude}" # Example coordinates (Berlin, Germany)

    # 2. Perform reverse geocoding
    location = geolocator.reverse(coordinates)

    return location.address if location else None # pyright: ignore[reportAttributeAccessIssue]
