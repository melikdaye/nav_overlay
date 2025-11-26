from fastapi import FastAPI
from playwright.async_api import async_playwright
import asyncio

app = FastAPI()

async def get_final_url(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except:
            pass  # Bazı URL'ler networkidle bekletmez

        # JavaScript redirect varsa yakalamak için kısa bekleme
        await asyncio.sleep(3)

        final_url = page.url
        await browser.close()
        return final_url


@app.get("/resolve")
async def resolve(url: str):
    final_url = await get_final_url(url)
    return {"final_url": final_url}
