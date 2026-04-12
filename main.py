import asyncio
import os
import zipfile
import requests
from playwright.async_api import async_playwright

# ========== إعدادات التيليجرام ==========
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
# =====================================

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
    print(f"\n📨 {msg[:50]}...")
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if img and os.path.exists(img):
            with open(img, "rb") as f:
                response = requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": msg}, files={"photo": f}, timeout=15)
        else:
            response = requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": msg}, timeout=15)
        if response.status_code == 200:
            print("✅ تم الإرسال.")
        else:
            print(f"❌ خطأ تيليجرام {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ استثناء: {e}")

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
        
        send_tg("🌐 فتح صفحة اللاب...")
        await page.goto(LAB_URL, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)
        
        await page.screenshot(path="before_signin.png")
        send_tg("📸 قبل تسجيل الدخول", "before_signin.png")
        
        # ========== 1. النقر على Sign in في الأعلى ==========
        signin_btn = page.locator("a:has-text('Sign in'), button:has-text('Sign in'), span:has-text('Sign in')").first
        
        if await signin_btn.count() > 0:
            send_tg("🔘 وجدت زر Sign in، جاري النقر...")
            await signin_btn.click()
            await page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(3)
            
            # ========== 2. انتظار صفحة sign_in والنقر على "Sign in with Google" ==========
            try:
                # انتظر ظهور زر "Sign in with Google" (قد يكون نصاً أو داخل link)
                google_signin_btn = page.locator("a:has-text('Sign in with Google'), button:has-text('Sign in with Google')").first
                await google_signin_btn.wait_for(state="visible", timeout=10000)
                await google_signin_btn.click()
                send_tg("🔘 تم النقر على 'Sign in with Google'")
                await page.wait_for_load_state("networkidle", timeout=30000)
                await asyncio.sleep(3)
            except Exception as e:
                send_tg(f"⚠️ لم يظهر زر 'Sign in with Google': {str(e)[:40]}")
                # ربما تم التوجيه مباشرة لقائمة الحسابات
                pass
            
            # ========== 3. انتظار قائمة اختيار الحساب ==========
            try:
                await page.wait_for_selector('div[data-email]', timeout=15000)
                accounts = page.locator('div[data-email]')
                target_account = accounts.filter(has_text="omarcora").first
                
                if await target_account.count() > 0:
                    send_tg("✅ وجدت حساب omarcora، جاري النقر عليه...")
                    await target_account.click()
                    await page.wait_for_load_state("networkidle", timeout=30000)
                    await asyncio.sleep(3)
                    send_tg("✅ تم اختيار الحساب. الآن يجب أن يتم تسجيل الدخول تلقائياً.")
                else:
                    send_tg("⚠️ لم يتم العثور على حساب يبدأ بـ omarcora. التقاط قائمة الحسابات...")
                    await page.screenshot(path="accounts_list.png")
                    send_tg("📸 قائمة الحسابات المتاحة", "accounts_list.png")
            except Exception as e:
                send_tg(f"⚠️ لم تظهر قائمة اختيار الحساب: {str(e)[:50]}")
            
            await page.screenshot(path="after_signin.png")
            send_tg("📸 بعد محاولة تسجيل الدخول", "after_signin.png")
        else:
            send_tg("ℹ️ زر Sign in غير موجود. ربما أنت مسجل الدخول مسبقاً.")
        
        # ========== 4. العودة إلى صفحة اللاب (إذا انتقلنا) ==========
        await asyncio.sleep(3)
        if "skills.google" not in page.url:
            send_tg("🔄 إعادة التوجيه لصفحة اللاب...")
            await page.goto(LAB_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)
        
        # ========== 5. الضغط على Start Lab ==========
        try:
            btn = page.locator("button:has-text('Start Lab'), button:has-text('بدء')").first
            await btn.wait_for(state="visible", timeout=10000)
            await btn.click()
            send_tg("🔘 تم الضغط على بدء المهمة.")
        except Exception:
            send_tg("ℹ️ زر البدء غير موجود. قد يكون اللاب بدأ تلقائياً.")
        
        # ========== 6. معالجة الكابتشا ==========
        await asyncio.sleep(5)
        try:
            await page.wait_for_selector("iframe[src*='recaptcha']", timeout=10000)
            anchor_frame = page.frame_locator("iframe[title='reCAPTCHA']").first
            await anchor_frame.locator(".recaptcha-checkbox-border").click(timeout=5000)
            await asyncio.sleep(3)
            
            challenge_frame = page.frame_locator("iframe[title*='recaptcha challenge']").first
            if await challenge_frame.locator("#rc-imageselect").count() > 0:
                send_tg("🤖 تحدي صور ظهر، جاري استخدام Buster...")
                await challenge_frame.locator("#solver-button").wait_for(state="visible", timeout=10000)
                await challenge_frame.locator("#solver-button").click()
                await asyncio.sleep(12)
                send_tg("✅ Buster قام بمحاولة الحل.")
        except Exception:
            send_tg("ℹ️ لم تظهر كابتشا.")
        
        await asyncio.sleep(5)
        await page.screenshot(path="final.png")
        send_tg(f"✅ المهمة انتهت.\nالرابط: {page.url}", "final.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
