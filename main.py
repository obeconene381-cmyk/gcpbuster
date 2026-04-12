import asyncio
import os
import zipfile
import requests
from playwright.async_api import async_playwright

# إعدادات التلجرام
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

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
    send_tg("🚀 بدأت المحاولة الجديدة. جاري تشغيل المتصفح...")
    ext_path = await get_ext()
    
    async with async_playwright() as p:
        browser = None
        try:
            # تشغيل المتصفح العادي (وليس Persistent Context)
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=500,
                args=[
                    f"--disable-extensions-except={ext_path}",
                    f"--load-extension={ext_path}",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--no-first-run",
                    "--disable-blink-features=AutomationControlled"
                ],
                timeout=300000  # 5 دقائق لبدء التشغيل
            )
            
            # إنشاء سياق جديد وإضافة الكوكيز
            context = await browser.new_context()
            await context.add_cookies(MY_COOKIES)
            page = await context.new_page()
            
            send_tg("🌐 راني نفتح في صفحة اللاب...")
            await page.goto(LAB_URL, wait_until="networkidle", timeout=90000)
            await asyncio.sleep(5)
            
            await page.screenshot(path="status.png")
            send_tg("📸 راني داخل الصفحة. شوف السكرين شوت:", "status.png")

            # الضغط على زر Start Lab
            btn = page.locator("button:has-text('Start Lab'), button:has-text('بدء')").first
            await btn.wait_for(state="visible", timeout=30000)
            await btn.click()
            send_tg("🔘 تم الضغط على زر البدء. جاري مراقبة الكبتشا...")

            # حل الكبتشا باستخدام Buster
            await asyncio.sleep(5)
            for frame in page.frames:
                if "api2/anchor" in frame.url:
                    await frame.click(".recaptcha-checkbox-border")
                    await asyncio.sleep(4)
                if "api2/bframe" in frame.url:
                    send_tg("🤖 لقيت الكبتشا! راني نفعّل في Buster...")
                    await frame.locator("#solver-button").click()
                    await asyncio.sleep(15)

            await asyncio.sleep(10)
            await page.screenshot(path="final.png")
            send_tg(f"✅ المهمة انتهت! الرابط الحالي:\n{page.url}", "final.png")

        except Exception as e:
            # التقاط صورة خطأ إن أمكن
            try:
                if browser and page:
                    await page.screenshot(path="error.png")
                    send_tg(f"❌ صرا مشكل: {str(e)[:100]}", "error.png")
                else:
                    send_tg(f"❌ فشل قبل فتح الصفحة: {str(e)[:100]}")
            except:
                send_tg(f"❌ صرا مشكل والمتصفح ما قدرش يصور: {str(e)[:100]}")
        finally:
            if browser:
                try: await browser.close()
                except: pass

if __name__ == "__main__":
    asyncio.run(run())
