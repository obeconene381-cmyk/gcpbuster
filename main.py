import asyncio
import os
import json
import zipfile
import requests
from playwright.async_api import async_playwright

# ==========================================
# بيانات التلجرام والروابط
# ==========================================
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

# الكوكيز التي أرسلتها (تذكرة الدخول)
COOKIES_LIST = [
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
    """فك ضغط إضافة Buster المرفوعة مسبقاً"""
    zip_path = "buster-main.zip"
    ext_path = "buster_ext"
    if not os.path.exists(zip_path):
        raise Exception("❌ لم يتم العثور على buster-main.zip في المستودع!")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(ext_path)
    
    # البحث عن المجلد الذي يحتوي على manifest.json
    for root, dirs, files in os.walk(ext_path):
        if "manifest.json" in files:
            return os.path.abspath(root)
    return os.path.abspath(ext_path)

async def run_automation():
    # 1. تجهيز الإضافة
    try:
        ext_full_path = await setup_extension()
        print(f"✅ تم تجهيز الإضافة في: {ext_full_path}")
    except Exception as e:
        send_telegram(f"❌ خطأ في الإضافة: {e}")
        return

    async with async_playwright() as p:
        # 2. تشغيل المتصفح مع الإضافة
        print("🚀 جاري تشغيل المتصفح...")
        context = await p.chromium.launch_persistent_context(
            "user_data",
            headless=False,
            args=[
                f"--disable-extensions-except={ext_full_path}",
                f"--load-extension={ext_full_path}",
                "--no-sandbox"
            ]
        )
        
        # 3. حقن الكوكيز (تسجيل الدخول التلقائي)
        await context.add_cookies(COOKIES_LIST)
        page = context.pages[0]

        try:
            # 4. الدخول لصفحة اللاب مباشرة
            print("🔗 الانتقال لرابط اللاب...")
            await page.goto(LAB_URL, wait_until="networkidle")
            await asyncio.sleep(5)

            # سكرين شوت للتأكد من الدخول بالحساب
            await page.screenshot(path="check_login.png")
            send_telegram("📸 سكرين شوت للتحقق من تسجيل الدخول بالكوكيز", "check_login.png")

            # 5. الضغط على Start Lab
            start_btn = page.get_by_role("button", name="Start Lab")
            if await start_btn.is_visible():
                await start_btn.click()
                print("🔘 تم الضغط على Start Lab.")
                await asyncio.sleep(5)

                # 6. التعامل مع الكبتشا بواسطة Buster
                print("🕵️ البحث عن كبتشا...")
                for frame in page.frames:
                    if "api2/anchor" in frame.url:
                        await frame.click(".recaptcha-checkbox-border")
                        await asyncio.sleep(4)
                
                for frame in page.frames:
                    if "api2/bframe" in frame.url:
                        print("🤖 تفعيل Buster لحل الكبتشا...")
                        # النقر على زر الإضافة داخل الكبتشا
                        await frame.click("#solver-button")
                        await asyncio.sleep(12) # وقت للحل

            # 7. انتظار بدء اللاب وإرسال الرابط النهائي
            print("⏳ انتظار نهائي لبدء اللاب...")
            await asyncio.sleep(15)
            
            final_url = page.url
            await page.screenshot(path="final_result.png")
            send_telegram(f"✅ تم تشغيل اللاب بنجاح!\n🔗 الرابط الحالي: {final_url}", "final_result.png")

        except Exception as e:
            await page.screenshot(path="error.png")
            send_telegram(f"❌ حدث خطأ أثناء الأتمتة:\n{str(e)[:200]}", "error.png")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_automation())
