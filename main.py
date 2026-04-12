import asyncio
import os
import json
import zipfile
import requests
from playwright.async_api import async_playwright

# إسكات تنبيهات النظام المزعجة
os.environ["DBUS_SESSION_BUS_ADDRESS"] = "/dev/null"

# إعدادات التلجرام والروابط
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

# الكوكيز الذهبية لي بعثتها نتا (الآن السكريبت عندو تصريح دخول كامل)
MY_COOKIES = [
    {"domain": ".google.com", "name": "__Secure-1PAPISID", "value": "UuI95bhHmuJTfRbY/AdsqK54C5qNUrOhdv", "path": "/", "secure": True},
    {"domain": ".google.com", "name": "__Secure-1PSID", "value": "g.a0008Ai6P4D9VxUMsensK1KpzeOc24d8VoHzO9H99BWH0mlOD6cmjs-BEg_YPf-HLWwDZdCefAACgYKAUISARMSFQHGX2MiwOJS0q3XWAy99YYvXGhGkhoVAUF8yKqoLEMDT5_IcXJDsfEymmDD0076", "path": "/", "secure": True, "httpOnly": True},
    {"domain": ".google.com", "name": "__Secure-3PAPISID", "value": "UuI95bhHmuJTfRbY/AdsqK54C5qNUrOhdv", "path": "/", "secure": True},
    {"domain": ".google.com", "name": "__Secure-3PSID", "value": "g.a0008Ai6P4D9VxUMsensK1KpzeOc24d8VoHzO9H99BWH0mlOD6cmKA7Vb--6_FUasiorXlEHzwACgYKAQ4SARMSFQHGX2MiBsvg0VZbiwoRKrmJdnrlXBoVAUF8yKo5RslT3ogoQDVliD4Ua80o0076", "path": "/", "secure": True, "httpOnly": True},
    {"domain": ".google.com", "name": "SID", "value": "g.a0008Ai6P4D9VxUMsensK1KpzeOc24d8VoHzO9H99BWH0mlOD6cmNAANXYlzTcpqDF3cHOeo4QACgYKAYgSARMSFQHGX2Miq4Sr8_RQAGM1RfiQnRkGtBoVAUF8yKrEeAB845ZqHKZcEyLv2YO20076", "path": "/", "secure": False},
    {"domain": ".google.com", "name": "HSID", "value": "AMy4_Ta2HCzvZSQE3", "path": "/", "secure": False, "httpOnly": True},
    {"domain": ".google.com", "name": "SSID", "value": "Adb8GZVQq7ZbRgy9X", "path": "/", "secure": True, "httpOnly": True},
    {"domain": ".google.com", "name": "SAPISID", "value": "UuI95bhHmuJTfRbY/AdsqK54C5qNUrOhdv", "path": "/", "secure": True},
    {"domain": "myaccount.google.com", "name": "OSID", "value": "g.a0007gi6PyETRCtIRHIthOjH1AMoPuTWNs3Vmk_q2ffnGit35WwoiNnR8xSA5FtWZ6AHtOMHtQACgYKAbASARMSFQHGX2MicG_A8MeAxMMWqeuG9awUbxoVAUF8yKoQE2UfitDk6VPiPH4S2ZPZ0076", "path": "/", "secure": True, "httpOnly": True}
]

def send_telegram(text, photo_path=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": text}, files={"photo": photo}, timeout=15)
        else:
            requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": text}, timeout=15)
    except: pass

async def setup_extension():
    """تجهيز إضافة Buster"""
    zip_path = "buster-main.zip"
    dest = "buster_dir"
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(dest)
        for r, d, f in os.walk(dest):
            if "manifest.json" in f: return os.path.abspath(r)
    return os.path.abspath(dest)

async def run_automation():
    send_telegram("🚀 بدأت العملية: جاري حقن الكوكيز الشاملة وفتح المتصفح...")
    ext_path = await setup_extension()
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            "user_data", 
            headless=False,
            args=[
                f"--disable-extensions-except={ext_path}", 
                f"--load-extension={ext_path}", 
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer"
            ]
        )
        
        # حقن الكوكيز في السياق (Context) لضمان تسجيل الدخول
        await context.add_cookies(MY_COOKIES)
        page = context.pages[0]
        page.set_default_timeout(60000)

        try:
            # التوجه مباشرة للاب
            send_telegram("🌐 جاري الدخول لرابط اللاب مباشرة...")
            await page.goto(LAB_URL, wait_until="domcontentloaded")
            await asyncio.sleep(7)
            
            # تصوير الصفحة للتأكد من تخطي تسجيل الدخول
            await page.screenshot(path="login_status.png")
            send_telegram("📸 الحالة: المفترض أننا داخل الحساب الآن ✅", "login_status.png")

            # الضغط على Start Lab
            start_btn = page.locator("button:has-text('Start Lab'), button:has-text('بدء')").first
            if await start_btn.is_visible():
                await start_btn.click()
                send_telegram("🔘 تم الضغط على Start Lab. جاري مراقبة الكبتشا...")
                await asyncio.sleep(5)
            else:
                send_telegram("⚠️ لم أجد زر Start Lab! ربما الكوكيز تحتاج تحديث أو الصفحة مختلفة.")

            # التعامل مع الكبتشا وإضافة Buster
            for frame in page.frames:
                if "api2/anchor" in frame.url:
                    await frame.click(".recaptcha-checkbox-border")
                    await asyncio.sleep(4)
                if "api2/bframe" in frame.url:
                    solver = frame.locator("#solver-button")
                    if await solver.is_visible():
                        await solver.click()
                        send_telegram("🔥 تم تفعيل Buster لحل الكبتشا...")
                        await asyncio.sleep(15)

            # انتظار نهائي
            await asyncio.sleep(15)
            await page.screenshot(path="final.png", full_page=True)
            send_telegram(f"✅ انتهت المهمة بنجاح!\nالرابط النهائي:\n{page.url}", "final.png")

        except Exception as e:
            await page.screenshot(path="error.png")
            send_telegram(f"❌ تعطل السكريبت: {str(e)[:200]}", "error.png")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_automation())
