import json
import os
from risk_engine import RiskEngine
from geopy.geocoders import Nominatim


class MapEngine:
    CACHE_FILE = "location_cache.json"

    @staticmethod
    def _load_cache():
        if os.path.exists(MapEngine.CACHE_FILE):
            with open(MapEngine.CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def _save_cache(cache):
        with open(MapEngine.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _resolve_location(location_name):
        cache = MapEngine._load_cache()

        if location_name in cache:
            return cache[location_name]

        geolocator = Nominatim(user_agent="fb_forensics_viewer")
        result = geolocator.geocode(location_name)

        if not result:
            return None

        coords = {
            "lat": result.latitude,
            "lon": result.longitude
        }

        cache[location_name] = coords
        MapEngine._save_cache(cache)

        return coords

    @staticmethod
    def get_grouped_login_points(logins):
        scored, _, _ = RiskEngine.calculate_risk_score(logins)

        grouped = {}

        for item in scored:
            location = item.get("location", "Unknown")
            coords = MapEngine._resolve_location(location)

            if not coords:
                continue

            if location not in grouped:
                grouped[location] = {
                    "location": location,
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "count": 0,
                    "details": [],
                    "levels": []
                }

            grouped[location]["count"] += 1
            grouped[location]["levels"].append(item.get("level", "LOW"))
            grouped[location]["details"].append(
                f"{item.get('date', 'N/A')} | IP: {item.get('ip', 'N/A')} | {item.get('level', 'LOW')}"
            )

        result = []

        for location, data in grouped.items():
            if "HIGH" in data["levels"]:
                summary_level = "HIGH"
            elif "MEDIUM" in data["levels"]:
                summary_level = "MEDIUM"
            else:
                summary_level = "LOW"

            result.append({
                "location": data["location"],
                "lat": data["lat"],
                "lon": data["lon"],
                "count": data["count"],
                "level": summary_level,
                "details": "\n".join(data["details"])
            })

        return result