import time
import re
import os
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def extract_latlon(url: str):
    pattern = r"@(-?\d+\.\d+),(-?\d+\.\d+),(\d+)z"
    m = re.search(pattern, url)
    if not m:
        return None
    return {
        "lat": float(m.group(1)),
        "lon": float(m.group(2)),
        "zoom": int(m.group(3))
    }

def resolve_google_maps(url: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1280,720")

    # IMPORTANT: Render'da Chrome path burasıdır
    chrome_options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(
        ChromeDriverManager().install(),
        options=chrome_options
    )

    driver.get(url)
    time.sleep(3)

    try:
        driver.execute_script("window.scrollBy(0, 1);")
        time.sleep(1)
        driver.execute_script("window.scrollBy(0, -1);")
        time.sleep(1)
    except:
        pass

    final_url = driver.current_url
    driver.quit()

    coords = extract_latlon(final_url)
    return final_url, coords


@app.get("/resolve")
def resolve():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "url param required"}), 400

    final_url, coords = resolve_google_maps(url)

    return jsonify({
        "final_url": final_url,
        "coordinates": coords
    })


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Google Maps resolver is running"
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
