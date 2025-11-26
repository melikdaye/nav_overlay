import time
import re
from flask import Flask, request, jsonify
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import os
import traceback

app = Flask(__name__)
app.debug = True  # Debug ON

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
    print(">>> Incoming URL:", url, flush=True)

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")

        print(">>> Launching Chrome...", flush=True)
        driver = uc.Chrome(options=chrome_options)

        print(">>> Navigating to URL...", flush=True)
        driver.get(url)
        time.sleep(3)

        print(">>> Current URL after load:", driver.current_url, flush=True)

        # Maps bazen URL güncellemez -> tetikle
        driver.execute_script("window.scrollBy(0, 1);")
        time.sleep(1)
        driver.execute_script("window.scrollBy(0, -1);")
        time.sleep(1)

        final_url = driver.current_url
        driver.quit()

        print(">>> Final URL:", final_url, flush=True)

        coords = extract_latlon(final_url)
        print(">>> Extracted coords:", coords, flush=True)

        return final_url, coords

    except Exception as e:
        print(">>> ERROR in resolve_google_maps:", e, flush=True)
        print(traceback.format_exc(), flush=True)
        raise


@app.get("/resolve")
def resolve():
    try:
        url = request.args.get("url")
        if not url:
            return jsonify({"error": "url param required"}), 400

        final_url, coords = resolve_google_maps(url)

        return jsonify({
            "final_url": final_url,
            "coordinates": coords
        })

    except Exception as e:
        print(">>> ERROR in /resolve handler:", e, flush=True)
        print(traceback.format_exc(), flush=True)
        return jsonify({"error": str(e)}), 500


@app.get("/")
def home():
    return {"status": "ok", "message": "resolver running", "debug": True}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
