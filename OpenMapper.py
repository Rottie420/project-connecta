import folium
from flask import render_template
import re

class OpenMapper:
    def __init__(self):
        pass

    def dms_to_decimal(self, dms_str):
        """
        Convert a DMS coordinate string to decimal degrees.
        """
        # Regular expression to extract the degree, minute, second, and direction
        match = re.match(r"(\d+)°(\d+)'([\d.]+)\"([NSEW])", dms_str)
        if not match:
            raise ValueError(f"Invalid DMS format: {dms_str}")
        
        degrees, minutes, seconds, direction = match.groups()
        decimal = int(degrees) + int(minutes) / 60 + float(seconds) / 3600
        if direction in 'SW':  # South and West are negative
            decimal *= -1
        return decimal

    def parse_coords(self, coords_str):
        """
        Parse a string of DMS coordinates into a tuple of decimal coordinates.
        Example input: "1°21'32.9\"N 103°55'57.8\"E"
        """
        # Split the input string by space to get latitude and longitude
        lat_str, lon_str = coords_str.split(' ')

        # Convert the latitude and longitude to decimal degrees
        lat = self.dms_to_decimal(lat_str)
        lon = self.dms_to_decimal(lon_str)
        
        # Return a list with one tuple containing the converted coordinates
        return [(lat, lon)]

    def render_map(self, coords_str):
        # Parse the coordinates from the string
        gps_coords = self.parse_coords(coords_str)

        # Create a map centered at the first coordinate
        if not gps_coords:
            raise ValueError("No coordinates provided.")

        m = folium.Map(location=gps_coords[0], zoom_start=6)

        # Add markers to the map
        for coord in gps_coords:
            folium.Marker(location=coord).add_to(m)

        # Save the map as an HTML file
        map_path = 'templates/map.html'
        m.save(map_path)

        # Render the map in a template
        return render_template('map.html')
