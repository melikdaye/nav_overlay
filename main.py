from fastapi import FastAPI
from playwright.async_api import async_playwright
import asyncio
import re

app = FastAPI()

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

async def get_final_url_and_coords(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )
        page = await browser.new_page()

        await page.goto(url, wait_until="networkidle", timeout=30000)

        # Maps URL yüklenmesi için bekleme
        await asyncio.sleep(2)

        # URL güncellenmiyorsa tetikle
        try:
            await page.keyboard.press("+")
            await asyncio.sleep(1)
        except:
            pass

        final_url = page.url    # <-- DOĞRUSU BU
        coords = extract_latlon(final_url)

        await browser.close()
        return final_url, coords

@app.get("/resolve")
async def resolve(url: str):
    final_url, coords = await get_final_url_and_coords(url)
    return {
        "final_url": final_url,
        "coordinates": coords
    }
