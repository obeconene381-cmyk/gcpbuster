import asyncio
import os
import zipfile
import requests
import traceback
from playwright.async_api import async_playwright

# إعدادات التلجرام
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

# الكوكيز تاعك (الصحاح)
MY_COOKIES = [
    {"domain": ".google.com", "name": "__Secure-1PAPISID", "value": "UuI95bhHmuJTfRbY/AdsqK54C5qNUrOhdv", "path": "/", "secure": True},
    {"domain": ".google.com", "name": "__Secure-1PSID", "value": "g.a0008Ai6P4D9VxUMsensK1KpzeOc24d8VoHzO9H99BWH0mlOD6cmjs-BEg_YPf-HLWwDZdCefAACgYKAUISARMSFQHGX2MiwOJS0q3XWAy99YYvXGhGkhoVAUF8yKqoLEMDT5_IcXJDsfEymmDD0076", "path": "/", "secure": True},
    {"domain": ".google.com", "name": "__Secure-3PAPISID", "value": "UuI95bhHmuJTfRbY/AdsqK54C5qNUrOhdv", "path": "/", "secure": True},
    {"domain": ".google.com", "name": "__Secure-3PSID", "value": "g.a0008Ai6P4D9VxUMsensK1KpzeOc24d8VoHzO9H99BWH0mlOD6cmKA7Vb--6_FUasiorXlEHzwACgYKAQ4SARMSFQHGX2MiBsvg0VZbiwoRKrmJdnrlXBoVAUF8yKo5RslT3ogoQDVliD4Ua80o0076", "path": "/", "secure": True},
    {"domain": ".google.com", "name": "SID", "value": "g.a0008Ai6P4D9VxUMsensK1KpzeOc24d8VoHzO9H99BWH0mlOD6cmNAANXYlzTcpqDF3cHOeo4QACgYKAYgSARMSFQHGX2Miq4Sr8_RQAGM1RfiQnRkGtBoVAUF8yKrEeAB845ZqHKZcEyLv2YO20076", "path": "/"},
    {"domain": ".google.com", "name": "HSID", "value": "AMy4_Ta2HCzvZSQE3", "path": "/"},
    {"domain": ".google.com", "name": "SSID", "value": "Adb8GZVQq7ZbRgy9X", "path": "/", "secure": True},
    {"domain": ".google.com", "name": "SAPISID", "value": "UuI95bhHmuJTfRbY/AdsqK54C5qNUrOhdv", "path": "/", "secure": True},
    {"domain": "myaccount.google.com", "name": "OSID", "value": "g.a0007gi6PyETRCtIRHIthOjH1AMoPuTWNs3Vmk_q2ffnGit35WwoiNnR8xSA5FtWZ6AHtOMHtQACgYKAbASARMSFQHGX2MicG_A8MeAxMMWqeuG9awUbxoVAUF8yKoQE2UfitDk6VPiPH4S2ZPZ0076", "path": "/", "secure": True}
]

def send_tg(msg, img=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if img:
            with open(img, "rb") as f: requests.post(url+"sendPhoto", data={"chat_id":CHAT_ID, "caption":msg}, files={"photo":f}, timeout=15)
        else:
            requests.post(url+"sendMessage", json={"chat_id":CHAT_ID, "text":msg}, timeout=15)
    except: pass

async def get_ext():
    zip_p = "buster-main.zip"
    dest = "ext_folder"
    if os.path.exists(zip_p):
        with zipfile.ZipFile(zip_p, 'r') as z: z.extractall(dest)
        for r, d, f in os.walk(dest):
            if "manifest.json" in f: return os.path.abspath(r)
    return os.path.abspath(dest)

async def run():
    send_tg("🔥 بدأ العمل! راني نوجد في المتصفح...")
    ext_path = await get_ext()
    
    async with async_playwright() as p:
        # تشغيل المتصفح بأوامر تمنع أي تعليق
        browser = await p.chromium.launch_persistent_context(
            "user_data", headless=False,
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage"
            ]
        )
        await browser.add_cookies(MY_COOKIES)
        page = browser.pages[0]
        page.set_default_timeout(60000)

        try:
            send_tg("🌐 راني نفتح في صفحة اللاب...")
            await page.goto(LAB_URL, wait_until="networkidle")
            await asyncio.sleep(5)
            await page.screenshot(path="login.png")
            send_tg("📸 دخلت! شوف التصويرة إذا راني مسجل الدخول.", "login.png")

            # الضغط على زر البدء
            btn = page.locator("button:has-text('Start Lab'), button:has-text('بدء')").first
            await btn.wait_for(state="visible")
            await btn.click()
            send_tg("🔘 ضغطت على Start Lab! جاري البحث عن الكبتشا...")
            await asyncio.sleep(5)

            # التعامل مع الكبتشا
            for f in page.frames:
                if "api2/anchor" in f.url:
                    await f.click(".recaptcha-checkbox-border")
                    await asyncio.sleep(4)
                if "api2/bframe" in f.url:
                    send_tg("🤖 لقيت الكبتشا! راني نخدم بـ Buster درك...")
                    await f.click("#solver-button")
                    await asyncio.sleep(15)

            await asyncio.sleep(10)
            await page.screenshot(path="final.png")
            send_tg(f"✅ كملت! الرابط: {page.url}", "final.png")

        except Exception as e:
            await page.screenshot(path="err.png")
            send_tg(f"❌ حبست هنا: {str(e)[:150]}", "err.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
