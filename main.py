import asyncio
import os
import zipfile
import requests
from playwright.async_api import async_playwright

# إعدادات التلجرام من المتغيرات البيئية
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
LAB_URL = os.environ.get("LAB_URL", "https://www.skills.google/focuses/19146?parent=catalog")

# قائمة الكوكيز (يجب تحديثها كل فترة)
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
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if img and os.path.exists(img):
            with open(img, "rb") as f:
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": msg}, files={"photo": f}, timeout=15)
        else:
            requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except Exception as e:
        print("Telegram error:", e)

async def get_ext():
    zip_p = "buster-main.zip"
    dest = "ext_folder"
    if os.path.exists(zip_p):
        with zipfile.ZipFile(zip_p, 'r') as z:
            z.extractall(dest)
        for r, d, f in os.walk(dest):
            if "manifest.json" in f:
                return os.path.abspath(r)
    return os.path.abspath(dest)

async def run():
    send_tg("🚀 بدأت المحاولة. جاري تجهيز المتصفح...")
    ext_path = await get_ext()
    
    async with async_playwright() as p:
        # تشغيل Chromium في وضع headless (ضروري لبيئة CI)
        browser = await p.chromium.launch(
            headless=True,
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--window-size=1280,720"
            ]
        )
        
        context = await browser.new_context()
        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()
        
        send_tg("🌐 جاري فتح صفحة اللاب...")
        await page.goto(LAB_URL, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)
        
        # التقاط صورة أولية
        await page.screenshot(path="status.png")
        send_tg("📸 تم فتح الصفحة بنجاح", "status.png")
        
        # الضغط على زر Start Lab
        try:
            btn = page.locator("button:has-text('Start Lab'), button:has-text('بدء')").first
            await btn.wait_for(state="visible", timeout=20000)
            await btn.click()
            send_tg("🔘 تم الضغط على بدء المهمة.")
        except Exception:
            send_tg("⚠️ لم يتم العثور على زر البدء، ربما اللاب مفتوح مسبقًا.")
        
        # بعد الضغط على زر Start Lab
        await asyncio.sleep(5)
        
        try:
            # انتظر وجود iframe reCAPTCHA
            await page.wait_for_selector("iframe[src*='recaptcha']", timeout=15000)
            
            # النقر على مربع "أنا لست روبوت"
            anchor_frame = page.frame_locator("iframe[title='reCAPTCHA']").first
            await anchor_frame.locator(".recaptcha-checkbox-border").click(timeout=10000)
            await asyncio.sleep(4)
            
            # البحث عن إطار التحدي
            challenge_frame = page.frame_locator("iframe[title*='recaptcha challenge']").first
            if await challenge_frame.locator("#rc-imageselect").count() > 0:
                send_tg("🤖 تحدي صور ظهر، جاري استخدام Buster...")
                # انتظر زر Buster (قد يكون داخل shadow DOM أحيانًا)
                await challenge_frame.locator("#solver-button").wait_for(state="visible", timeout=10000)
                await challenge_frame.locator("#solver-button").click()
                await asyncio.sleep(12)
                send_tg("✅ Buster قام بمحاولة الحل.")
            else:
                send_tg("ℹ️ لم يظهر تحدي، ربما تم التحقق تلقائيًا.")
                
        except Exception as e:
            send_tg(f"⚠️ خطأ في معالجة الكابتشا: {str(e)[:80]}")
        
        # صورة نهائية
        await page.screenshot(path="final.png")
        send_tg(f"✅ المهمة انتهت.\nالرابط الحالي: {page.url}", "final.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
