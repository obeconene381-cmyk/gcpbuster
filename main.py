import asyncio
import os
import zipfile
import requests
import re
from playwright.async_api import async_playwright

# ========== إعدادات التيليجرام ==========
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
# =====================================

LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"
TARGET_EMAIL = "omarcora21@gmail.com"

MY_COOKIES = [
    # قائمة الكوكيز (من الأفضل تحديثها)
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

async def click_button_by_text_anywhere(page, text, exact=False, timeout_loop=30, post_click_wait=3):
    pattern = re.compile(rf"^\s*{re.escape(text)}\s*$", re.I) if exact else re.compile(re.escape(text), re.I)
    async def _post_click_stabilize():
        try: await page.wait_for_load_state("domcontentloaded", timeout=2000)
        except: pass
        await asyncio.sleep(post_click_wait)

    for _ in range(timeout_loop):
        for target in [page] + list(page.frames):
            try:
                locators = [
                    target.get_by_role("button", name=pattern),
                    target.get_by_role("link", name=pattern),
                    target.locator(f"button:has-text('{text}')"),
                    target.locator(f"a:has-text('{text}')"),
                    target.locator(f"[role='button']:has-text('{text}')"),
                ]
                for loc in locators:
                    for i in range(await loc.count()):
                        btn = loc.nth(i)
                        if await btn.is_visible() and await btn.is_enabled():
                            await btn.scroll_into_view_if_needed(timeout=1000)
                            await btn.click(timeout=3000, force=True)
                            await _post_click_stabilize()
                            return True
            except: pass
        await asyncio.sleep(1)
    return False

async def run():
    send_tg("🚀 بدأت المحاولة باستخدام Firefox + Stealth...")
    ext_path = await get_ext()
    
    async with async_playwright() as p:
        # استخدام Firefox بدلاً من Chromium
        browser = await p.firefox.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1280,720"
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            accept_downloads=True,
        )
        
        # تطبيق stealth عبر إزالة خصائص webdriver
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()
        
        send_tg("🌐 فتح صفحة اللاب...")
        await page.goto(LAB_URL, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)
        
        await page.screenshot(path="before_signin.png")
        send_tg("📸 قبل تسجيل الدخول", "before_signin.png")
        
        # 1. النقر على Sign in في الأعلى
        signin_clicked = await click_button_by_text_anywhere(page, "Sign in", exact=True, timeout_loop=10)
        if signin_clicked:
            send_tg("✅ تم النقر على Sign in")
            await asyncio.sleep(3)
        else:
            send_tg("ℹ️ زر Sign in غير موجود.")
        
        # 2. النقر على "Sign in with Google"
        google_clicked = await click_button_by_text_anywhere(page, "Sign in with Google", exact=False, timeout_loop=15)
        if google_clicked:
            send_tg("✅ تم النقر على Sign in with Google")
        else:
            send_tg("⚠️ لم يتم العثور على زر Sign in with Google")
            await page.screenshot(path="no_google_btn.png")
            send_tg("📸 صورة الصفحة", "no_google_btn.png")
        
        await asyncio.sleep(4)
        
        # 3. انتظار صفحة الحسابات
        account_page = None
        for p in context.pages:
            if "accounts.google.com" in p.url:
                account_page = p
                break
        
        if account_page:
            send_tg(f"🪟 تم فتح صفحة الحسابات: {account_page.url[:60]}")
            page = account_page
            await page.wait_for_load_state("networkidle", timeout=30000)
        else:
            send_tg("ℹ️ لم تظهر نافذة منفصلة.")
        
        # 4. محاولة إدخال البريد الإلكتروني
        try:
            email_input = page.locator("input[type='email'], input[name='identifier'], #identifierId").first
            await email_input.wait_for(state="visible", timeout=10000)
            await email_input.fill(TARGET_EMAIL)
            send_tg(f"📧 تم إدخال البريد: {TARGET_EMAIL}")
            
            next_clicked = await click_button_by_text_anywhere(page, "Next", exact=True, timeout_loop=10)
            if next_clicked:
                send_tg("✅ تم النقر على Next")
                await asyncio.sleep(4)
                
                try:
                    pass_input = page.locator("input[type='password']").first
                    await pass_input.wait_for(state="visible", timeout=5000)
                    send_tg("⚠️ تم طلب كلمة المرور! الكوكيز غير صالحة أو الحساب محمي.")
                    await page.screenshot(path="password_required.png")
                    send_tg("📸 مطلوب كلمة مرور", "password_required.png")
                except:
                    send_tg("✅ لم يُطلب كلمة مرور (تم التحقق تلقائياً).")
            else:
                send_tg("⚠️ لم يتم العثور على زر Next")
        except Exception as e:
            send_tg(f"ℹ️ لم يظهر حقل البريد: {str(e)[:40]}")
            # ربما ظهرت قائمة الحسابات
            try:
                accounts = page.locator('div[data-email], div[data-identifier]')
                target = accounts.filter(has_text="omarcora").first
                if await target.count() > 0:
                    await target.click()
                    send_tg("✅ تم اختيار حساب omarcora من القائمة")
                    await asyncio.sleep(4)
            except:
                pass
        
        # 5. العودة إلى صفحة اللاب
        lab_page = None
        for p in context.pages:
            if "skills.google" in p.url and "sign_in" not in p.url:
                lab_page = p
                break
        if lab_page:
            page = lab_page
            await page.bring_to_front()
            send_tg("🔄 عدنا إلى صفحة اللاب")
        else:
            send_tg("🔄 إعادة فتح صفحة اللاب...")
            await page.goto(LAB_URL, wait_until="networkidle", timeout=60000)
        
        await page.screenshot(path="after_signin.png")
        send_tg("📸 بعد تسجيل الدخول", "after_signin.png")
        
        # 6. الضغط على Start Lab
        start_clicked = await click_button_by_text_anywhere(page, "Start Lab", exact=False, timeout_loop=10)
        if not start_clicked:
            start_clicked = await click_button_by_text_anywhere(page, "بدء", exact=False, timeout_loop=5)
        if start_clicked:
            send_tg("🔘 تم الضغط على بدء المهمة")
        else:
            send_tg("ℹ️ زر البدء غير موجود")
        
        # 7. معالجة الكابتشا
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
