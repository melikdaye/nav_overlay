from flask import Flask, request, jsonify
import requests
import re
import os

app = Flask(__name__)

def resolve_short_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=5)
        return r.url
    except:
        return None


def extract_gmaps_coords(url: str):
    # METHOD 1: !3dLAT !4dLON  (EN DOĞRU)
    m1 = re.search(r'!3d([0-9\.\-]+)!4d([0-9\.\-]+)', url)
    if m1:
        lat = float(m1.group(1))
        lon = float(m1.group(2))
        return lat, lon

    # METHOD 2: @LAT,LON,
    m2 = re.search(r'@([0-9\.\-]+),([0-9\.\-]+)', url)
    if m2:
        lat = float(m2.group(1))
        lon = float(m2.group(2))
        return lat, lon

    # METHOD 3: embed !2dLON !3dLAT
    lon_match = re.search(r'!2d([0-9\.\-]+)', url)
    lat_match = re.search(r'!3d([0-9\.\-]+)', url)
    if lat_match and lon_match:
        lat = float(lat_match.group(1))
        lon = float(lon_match.group(1))
        return lat,lon

    return None


@app.get("/resolve")
def resolve():
    try:
        url = request.args.get("url")
        if not url:
            return jsonify({"error": "url required"}), 400
    
        long_url = resolve_short_url(url)
        if not long_url:
            return jsonify({"error": "cannot resolve short url"}), 500
    
        coords = extract_gmaps_coords(long_url)
        if not coords:
            return jsonify({"error": "cannot extract coordinates"}), 500
    
        lat, lon = coords

        return jsonify({"final_url": long_url, 
                "coordinates": {"lat": float(lat), "lon": float(lon), "zoom": 15}})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/")
def home():
    return {"status": "running", "version": "ultra_fast_1.0"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
