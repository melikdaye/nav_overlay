import time
import re
import os
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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



def get_google_share_link(url):

    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"

    # *** Hız Optimizasyonları ***
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--window-size=800,600")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--metrics-recording-only")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--dns-prefetch-disable")
    chrome_options.add_argument("--disk-cache-size=0")
    chrome_options.add_argument("--disable-features=TranslateUI")

    # ASCII output minimize
    os.environ["WDM_LOG_LEVEL"] = "0"

    # *** Chromedriver container içine build sırasında kurulmuş olacak ***
    service = Service("/usr/local/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Lite mode: Maps çok daha hızlı yüklenir
    if "?" in url:
        url += "&force=lite"
    else:
        url += "?force=lite"

    driver.get(url)
    time.sleep(0.5)

    # 2) Paylaş butonunu bul
    share_btn = driver.find_element(
        By.CSS_SELECTOR,
        "button[aria-label*='Paylaş'], button[aria-label*='Share']"
    )
    share_btn.click()
    time.sleep(1)

    # 3) Popup’taki link inputunu bul
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
