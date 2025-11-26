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

app = Flask(__name__)

def extract_latlon(url: str):
    pattern = r"@(-?\d+\.\d+),(-?\d+\.\d+),(\d+)z"
    m = re.search(pattern, url)
    if not m:
        return None
    return {"lat": float(m.group(1)), "lon": float(m.group(2)), "zoom": int(m.group(3))}

def resolve_google_maps(url: str):

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

    try:
        # Map canvas yüklenene kadar max 2.5 saniye bekle
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "canvas"))
        )
    except:
        pass

    # URL güncellemesi için hızlı scroll hack (çok hızlı)
    try:
        driver.execute_script("window.scrollBy(0,2);")
        time.sleep(0.01)
        driver.execute_script("window.scrollBy(0,-2);")
        #time.sleep(0.01)
    except:
        pass

    final_url = driver.current_url
    coords = extract_latlon(final_url)

    driver.quit()

    return final_url, coords


@app.get("/resolve")
def resolve():
    try:
        url = request.args.get("url")
        if not url:
            return jsonify({"error": "url param required"}), 400

        final_url, coords = resolve_google_maps(url)

        return jsonify({"final_url": final_url, "coordinates": coords})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/")
def home():
    return {"status": "running", "version": "ultra_fast_1.0"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
