import time
import re
import os
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests

app = Flask(__name__)

def resolve_short_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=5)
        return r.url
    except:
        return None

def extract_coords_from_url(url):
    match = re.search(r'!3d([0-9.\-]+)!4d([0-9.\-]+)', url)
    if match:
        lat = float(match.group(1))
        lon = float(match.group(2))
        return lat, lon
    return None



def get_google_share_link(initial_url: str):

    chrome_options = Options()

    # Headless = new
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1600,1200")
    chrome_options.add_argument("--start-maximized")

    chrome_options.add_argument("--disable-features=LiteMode")
    chrome_options.add_argument("--disable-features=IsolateOrigins,SitePerProcess")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Masaüstü user-agent kullan
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Maps Lite UI engelleme
    chrome_options.add_argument("--disable-features=IsolateOrigins,SitePerProcess,TranslateUI")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(initial_url)
    time.sleep(3)

    # Google bazen cookie banner veriyor
    try:
        agree_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Tümünü kabul et'], button[aria-label*='Accept all']")
        agree_btn.click()
        time.sleep(1)
    except:
        pass

    # Paylaş / Share butonunu bul
    share_btn = driver.find_element(
        By.CSS_SELECTOR,
        "button[aria-label*='Paylaş'], button[aria-label*='Share']"
    )
    share_btn.click()
    time.sleep(1.2)

    # Popup'taki input
    input_box = driver.find_element(By.CSS_SELECTOR, "input.vrsrZe")
    short_link = input_box.get_attribute("value")

    driver.quit()
    return short_link

def resolve_coordinates(url):

    # A) Selenium → resmi Share URL'ini al
    share_short = get_google_share_link(url)

    # B) Redirect ile uzun linki al
    final = requests.get(share_short, allow_redirects=True, timeout=10)
    long_url = final.url

    # C) POI koordinatı çıkar
    coords = extract_coords_from_url(long_url)
    if not coords:
        return None

    lat, lon = coords

    return {
        "final_url": long_url,
        "coordinates": {"lat": float(lat), "lon": float(lon), "zoom": 15}
    }

@app.get("/resolve")
def api_resolve():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "url required"}), 400

    try:
        result = resolve_coordinates(url)
        if not result:
            return jsonify({"error": "coordinates not found"}), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.get("/")
def home():
    return {"status": "running", "version": "ultra_fast_1.0"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
