import overpy
import geopy
from geopy.geocoders import Nominatim

# --- 1. ONE-TIME SETUP ---
geolocator = Nominatim(user_agent="carecompass_hackathon_app")
overpass_api = overpy.Overpass()

# --- 2. THE NEW FUNCTION ---
def find_local_facilities(location_query: str, required_resource: str) -> list:
    """
    Finds real-world facilities using the FREE OpenStreetMap/Overpass API.
    """
    print(f"[Tool Call: find_local_facilities] Searching OSM near '{location_query}'")
    
    try:
        # --- Step 1: Geocode the location ---
        location = geolocator.geocode(location_query)
        if not location:
            return {"error": "Location not found."}
        
        lat = location.latitude
        lon = location.longitude
        print(f"[Tool Call: find_local_facilities] Location found: ({lat}, {lon})")

        # --- Step 2: Build an Overpass query ---
        if required_resource == "ER":
            query_filter = 'node["amenity"="hospital"]'
        else: # "Doctor", "X-ray", "Stitches"
            query_filter = 'node["amenity"~"hospital|clinic|doctors"]'

        query = f"""
        [out:json];
        (
          {query_filter}(around:10000, {lat}, {lon});
        );
        out body;
        """

        # --- Step 3: Call the Overpass API ---
        result = overpass_api.query(query)
        
        # --- Step 4: Parse the results ---
        facilities_list = []
        for node in result.nodes:
            # We must have a name for it to be useful
            name = node.tags.get("name")
            if not name:
                continue

            facilities_list.append({
                "place_id": str(node.id),
                "name": name,
                "address": f"{node.tags.get('addr:housenumber', '')} {node.tags.get('addr:street', '')}",
                "rating": "N/A", # OSM doesn't have ratings
                "is_open": node.tags.get("opening_hours", "Unknown")
            })
            if len(facilities_list) >= 5: # Limit to 5
                break
        
        print(f"[Tool Call: find_local_facilities] Found {len(facilities_list)} facilities.")
        return facilities_list

    except Exception as e:
        print(f"Error in OpenStreetMap API call: {e}")
        return {"error": f"OSM API failed: {e}"}