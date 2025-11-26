import time
import re
from flask import Flask, request, jsonify
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

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

    driver = uc.Chrome(options=chrome_options)

    driver.get(url)
    time.sleep(3)

    # Maps bazen URL değiştirmez → hareket tetikleyelim
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


if __name__ == "__main__":
    # Render default PORT env değişkeni kullanır
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
