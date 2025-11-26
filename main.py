from fastapi import FastAPI
from playwright.async_api import async_playwright
import asyncio
import re

app = FastAPI()

def extract_latlon(url: str):
    """
    URL içinde @40.12345,29.54321,15z yapısını yakalar.
    """
    pattern = r"@(-?\d+\.\d+),(-?\d+\.\d+),(\d+)z"
    match = re.search(pattern, url)
    if not match:
        return None

    lat = float(match.group(1))
    lon = float(match.group(2))
    zoom = int(match.group(3))

    return {"lat": lat, "lon": lon, "zoom": zoom}


async def get_final_url_and_coords(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, wait_until="networkidle")

        # Maps URL'in güncellenmesi için 1–2 saniye bekle
        await asyncio.sleep(2)

        # Bazı Maps kısa URL'lerde otomatik güncelleme olmaz — ufak bir zoom/pan tetikleyelim
        try:
            await page.keyboard.press("+")
            await asyncio.sleep(1)
        except:
            pass

        final_url = page.url()
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
