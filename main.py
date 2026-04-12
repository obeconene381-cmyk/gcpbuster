import asyncio
import os
import zipfile
import requests
import traceback
from playwright.async_api import async_playwright

# ==========================================
# إعداداتك الخاصة
# ==========================================
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

# الكوكيز الخاصة بك لتخطي تسجيل الدخول
MY_COOKIES = [
    {"domain": ".skills.google", "name": "_ga", "value": "GA1.1.1438878037.1772447126", "path": "/"},
    {"domain": ".skills.google", "name": "_ga_2X30ZRBDSG", "value": "GS2.1.s1775983728$o96$g1$t1775984667$j31$l0$h0", "path": "/"},
    {"domain": "www.skills.google", "name": "_cvl-4_1_14_session", "value": "TT6WSZeZPt3w8HnK1t%2FZAv3Kn4geekpifkFOlEj61sEdgJWk1ml3FW6WeEJg2KTZmv75COjRA2bKSWLgRxa6gMglsaWCa%2FAoS8OfZyHmFo5%2BcGhKyf7YamK6ovWGqSrbgSWFv9Dmal2vKNtJTt2pLN3Qu%2F4XF3Ctp5hnm5PZyk2HuoeauJ0w1THJvnyz9LSaNsbMZAt3Pdy1V2pUxIgC0sfUsbk%2BhObj23ns7%2Fw029j1J2mrxcC%2B4HUFR9gk%2B9nztEz2c0mvs%2FjicosHIUFveRwfbSxr%2BB4zHgoB228m7REuPZboCvt5lxjxBHD6%2BnYLiykOySWzbzWpg0ifwAuE5mFKzg1ybG3hkWaeQBPR34J2bljFy72cEvZVe%2FYinyY%2FVCQOfSvMTkR%2BQ9EWaDEvaukUmItwPpF4uFto4MZFCsYTSBH7JFm%2BEyX%2Fq7mS7VNlxUcd%2BNQguZdEGDQQvBHssrL8KPnsYr1yIjJBwkDcjiHmvdjYKGdy0kcMfyOPUuUgV3KPe%2B2OpdyRkHctDRwsI23WaDpYWdNMCtQnZ6hWgueNozKDpTld9PjgCOY6QXovKmY43I7gbTgQT70Pk25wdCjiwYe31QXSvfFPRzNoqkWyqhdjoAfj4Twda4F3t%2B0%2BA4PIH8yeR8aT576WYZMQFAcIJNFVcOGBB1aYsFlqq0UpDR1n49mz2RC%2BuDc%2FwODy8FwKrOb1hBb0xNII9vmOu62DSXB0eFvHxvfmPbb7Swdag7GDg3FESjpNCeZ5eUHx3GNFHBh%2B6Q%3D%3D--2%2B3NRg1T54xp77Gi--9AN2nfZufYW1gTCaiAME%2Fw%3D%3D", "path": "/", "secure": True, "httpOnly": True},
    {"domain": "www.skills.google", "name": "browser.timezone", "value": "Africa/Algiers", "path": "/"},
    {"domain": "www.skills.google", "name": "user.expires_at", "value": "eyJfcmFpbHMiOnsibWVzc2FnZSI6IklqSXdNall0TURRdE1USlVNRGM2TURRNk1qQXVNalF4TFRBME9qQXdJZz09IiwiZXhwIjpudWxsLCJwdXIiOiJjb29raWUudXNlci5leHBpcmVzX2F0In19--4a24a03d83aefd10698e5f9459d29940ea3869bf", "path": "/", "secure": True},
    {"domain": "www.skills.google", "name": "user.id", "value": "eyJfcmFpbHMiOnsibWVzc2FnZSI6Ik1UTTNOREV5TlRZeSIsImV4cCI6bnVsbCwicHVyIjoiY29va2llLnVzZXIuaWQifX0%3D--39bb2ae5eaed2cb85e3fbf6cbf126e1d2448803d", "path": "/", "secure": True}
]

def send_telegram(text, photo_path=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": text}, files={"photo": photo})
        else:
            requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": text})
    except: pass

async def setup_extension():
    zip_path = "buster-main.zip"
    dest = "buster_dir"
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(dest)
        for r, d, f in os.walk(dest):
            if "manifest.json" in f: return os.path.abspath(r)
    return os.path.abspath(dest)

async def run_automation():
    ext_path = await setup_extension()
    
    async with async_playwright() as p:
        print("🛠️ تشغيل المتصفح...")
        # الأوامر الجديدة هنا لمنع انهيار كرت الشاشة (GPU)
        context = await p.chromium.launch_persistent_context(
            "user_data", 
            headless=False,
            args=[
                f"--disable-extensions-except={ext_path}", 
                f"--load-extension={ext_path}", 
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",                 # يمنع انهيار المتصفح في سيرفرات لينكس
                "--disable-software-rasterizer"  # يمنع انهيار المتصفح في سيرفرات لينكس
            ]
        )
        
        await context.add_cookies(MY_COOKIES)
        page = context.pages[0]
        page.set_default_timeout(60000)

        try:
            print("🌐 الانتقال إلى رابط اللاب...")
            await page.goto(LAB_URL, wait_until="domcontentloaded")
            await asyncio.sleep(5)

            await page.screenshot(path="step1.png")
            send_telegram("1. سكرين شوت: تم الدخول بالكوكيز وتجاوزنا خطأ GPU بنجاح ✅", "step1.png")

            print("🔘 الضغط على Start Lab...")
            start_btn = page.get_by_role("button", name="Start Lab")
            await start_btn.wait_for(state="visible")
            await start_btn.click()
            await asyncio.sleep(3)

            print("🕵️ البحث عن الكبتشا...")
            for frame in page.frames:
                if "api2/anchor" in frame.url:
                    await frame.click(".recaptcha-checkbox-border")
                    await asyncio.sleep(3)
                if "api2/bframe" in frame.url:
                    solver = frame.locator("#solver-button")
                    if await solver.is_visible():
                        await solver.click()
                        print("🤖 تم تفعيل Buster لحل الكبتشا.")
                        await asyncio.sleep(12)

            print("⏳ انتظار نهائي لتجهيز السيرفر...")
            await asyncio.sleep(15)
            
            await page.screenshot(path="final.png")
            send_telegram(f"✅ اكتملت المهمة بنجاح!\nالرابط: {page.url}", "final.png")

        except Exception as e:
            # إذا حدث أي خطأ الآن، سيتم إرسال تفاصيله للتلجرام فوراً!
            error_details = traceback.format_exc()
            await page.screenshot(path="error.png")
            send_telegram(f"❌ حدث خطأ برمجي:\n{error_details[-300:]}", "error.png")
            print(error_details)
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_automation())
