import asyncio
import os
import zipfile
import requests
import re
import shutil
import json
from playwright.async_api import async_playwright

# --- الإعدادات ---
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"
BUSTER_ZIP_URL = "https://github.com/dessant/buster/archive/refs/heads/master.zip"

WORKING_PROXY = {
    "server": "http://92.119.128.15:9996",
    "username": "user376353",
    "password": "y3ld6w"
}

CHROME_MANIFEST_CONTENT = {
  "manifest_version": 3,
  "name": "__MSG_extensionName__",
  "description": "__MSG_extensionDescription__",
  "version": "0.1.0",
  "author": "Armin Sebastian",
  "homepage_url": "https://github.com/dessant/buster",
  "default_locale": "en",
  "minimum_chrome_version": "123.0",
  "permissions": ["storage", "notifications", "webRequest", "declarativeNetRequest", "webNavigation", "nativeMessaging", "offscreen", "scripting"],
  "host_permissions": ["<all_urls>"],
  "content_security_policy": {
    "extension_pages": "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src * data:; connect-src *; object-src 'none'; frame-ancestors http://127.0.0.1:*;"
  },
  "icons": {
    "16": "src/assets/icons/app/icon-16.png", "48": "src/assets/icons/app/icon-48.png", "128": "src/assets/icons/app/icon-128.png"
  },
  "action": {
    "default_icon": { "16": "src/assets/icons/app/icon-16.png", "48": "src/assets/icons/app/icon-48.png", "128": "src/assets/icons/app/icon-128.png" }
  },
  "options_ui": { "page": "src/options/index.html", "open_in_tab": True },
  "background": { "service_worker": "src/background/script.js" },
  "content_scripts": [
    {
      "matches": ["https://*.google.com/recaptcha/*", "https://*.recaptcha.net/*"],
      "all_frames": True, "run_at": "document_idle", "css": ["src/base/style.css"], "js": ["src/base/script.js"]
    }
  ],
  "web_accessible_resources": [
    { "resources": ["src/setup/index.html", "src/scripts/reset.js", "src/base/solver-button.css"], "matches": ["http://*/*", "https://*/*"], "use_dynamic_url": True }
  ],
  "incognito": "split"
}

MY_COOKIES = [
    {"domain": ".skills.google", "name": "_ga", "value": "GA1.1.1438878037.1772447126", "path": "/"},
    {"domain": ".skills.google", "name": "_ga_2X30ZRBDSG", "value": "GS2.1.s1775996404$o97$g1$t1775996563$j32$l0$h0", "path": "/"},
    {"domain": "www.skills.google", "name": "_cvl-4_1_14_session", "value": "lQa%2FMnKdErx31nYRawt27XpphO7RO1Mod3%2FCk8T6PqZfkPZohBUhjBqhs2Mw1GIO229gr0KDHGkAp%2F9o7Blffpj%2BNy7YVlSwMKrQX3%2B0RxdyBzB0LU%2BFdcq5wLCPFWUPMhJNMngGjgVjse8JNXc1BO1j2FUpFQqvzAVGdPUShDJMshUZOva39naRS%2BVT%2BpBdaPE0I%2FgjsG6fC6KFeGqADXbUOQ36JiZQkoXYIjuKCxrOKwyaLKj7fFRebXiBduQKQIH3JK8bvcn0LkvK8BuvZ262zjAku4%2FkzRdFKfsfQMXrZStwGytxy1dqm%2FoQ6Lut8s9fnFVTGGcYIoJoxwba0Yx653S2FCemxd3GSCCqfGuNfuzRfNSCjsYvAeUmPdkQzepE80F3hbK15UUyM%2B2Puh3e4e%2FoovbnYf0xLZFGrxSpTcgJ5zb1FElGZ9LNFypWppJjbPlIySkS6X00pjko3fzmpi2TmUHvdBfPbn7ZmJbQ%2Fa8mQzvispzCN8GaAavsOZ%2FsD6xOt0%2FukYWX4oyXfRQg8AP8iZvYkj1iOvsbagPMKjp7utfL9DzDJ5n7LorhayjfSh9XLi1us38cm%2Fu8fzdbvLJn0DJ7koAN2V8V2KKLiGrU2H3e2z4pAFvTAmFENKac3LdIOOs2oNNj2Z8yF0iEnprV%2FzPeOb7eCcvFU66A6qb3f4SgUOTFVchEXizCrTx0%2FvdEQhoQG%2Boc3WXvnYtDbpPIuyt0BJSUda0e63hfWvQnww7DjHcdLtchLMoGYyOW0UktBRGkG3s%3D--TF35bd8CfnDqO%2BYr--Bp220SPOMrUj1y6NmvAiVw%3D%3D", "path": "/", "secure": True, "httpOnly": True},
    {"domain": "www.skills.google", "name": "user.id", "value": "eyJfcmFpbHMiOnsibWVzc2FnZSI6Ik1UTTNOVE13TmpJMyIsImV4cCI6bnVsbCwicHVyIjoiY29va2llLnVzZXIuaWQifX0%3D--3706d9f3abb091776145342b4e9be6e645941d44", "path": "/", "secure": True},
]

def send_tg(msg, img=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if img and os.path.exists(img):
            with open(img, "rb") as f:
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": msg}, files={"photo": f}, timeout=30)
        else:
            requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": msg}, timeout=30)
    except Exception as e: pass

async def setup_buster():
    target_dir = os.path.join(os.getcwd(), "buster_auto")
    zip_path = "buster_temp.zip"
    
    try:
        send_tg("📥 جاري تحميل كود الإضافة...")
        response = requests.get(BUSTER_ZIP_URL, timeout=30)
        with open(zip_path, "wb") as f:
            f.write(response.content)
            
        if os.path.exists(target_dir): shutil.rmtree(target_dir)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        os.remove(zip_path)
        
        # البحث عن المجلد الأساسي الذي *يحتوي* على src وليس الدخول لـ src
        root_path = None
        for root, dirs, files in os.walk(target_dir):
            if "src" in dirs:
                root_path = root
                break
                
        if root_path:
            # وضع ملف manifest.json في المجلد الأساسي (خارج src) لكي تعمل المسارات داخله
            manifest_path = os.path.join(root_path, "manifest.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(CHROME_MANIFEST_CONTENT, f, indent=2)
            
            # نسخ اللغات 
            locales_src = os.path.join(root_path, "src", "assets", "locales")
            locales_dest = os.path.join(root_path, "_locales")
            if os.path.exists(locales_src) and not os.path.exists(locales_dest):
                shutil.copytree(locales_src, locales_dest)

            send_tg(f"🛠️ تم إعداد الإضافة بشكل صحيح في المسار: {root_path}")
            return os.path.abspath(root_path)
                
        return None
    except Exception as e:
        send_tg(f"❌ خطأ في الإعداد: {e}")
        return None

# ==========================================
# تم استرجاع دوال الضغط الخاصة بك 100% كما أرسلتها في أول رسالة
# ==========================================
async def human_click(page, locator):
    """محاكاة النقر البشري"""
    try:
        await locator.scroll_into_view_if_needed()
        box = await locator.bounding_box()
        if box:
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            await page.mouse.move(x, y, steps=10)
            await asyncio.sleep(0.2)
            await page.mouse.down()
            await asyncio.sleep(0.15)
            await page.mouse.up()
            return True
        else:
            await locator.click(delay=200)
            return True
    except:
        try:
            await locator.click(force=True, delay=200)
            return True
        except:
            return False

async def click_start_lab_button(page):
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)
    for _ in range(60):
        try:
            btns = page.get_by_role("button", name=pattern)
            if await btns.count() > 0:
                b = btns.first
                if await b.is_visible():
                    await b.click(force=True)
                    send_tg("✅ تم النقر على Start Lab")
                    return True
        except:
            pass
        
        for frame in page.frames:
            try:
                btns = frame.get_by_role("button", name=pattern)
                if await btns.count() > 0:
                    b = btns.first
                    if await b.is_visible():
                        await b.click(force=True)
                        send_tg("✅ تم النقر على Start Lab (iframe)")
                        return True
            except:
                continue
        await asyncio.sleep(1)
    return False

async def click_captcha_checkbox(page):
    send_tg("🤛 البحث عن مربع الكابتشا...")
    try:
        await asyncio.sleep(3)
        iframes = await page.locator('iframe[title*="reCAPTCHA"], iframe[src*="recaptcha"]').all()
        
        for iframe in iframes:
            try:
                frame_content = iframe.content_frame
                checkbox = frame_content.locator('.recaptcha-checkbox-border').first
                if await checkbox.count() > 0 and await checkbox.is_visible():
                    await human_click(page, checkbox)
                    send_tg("✅ تم الضغط على المربع")
                    await asyncio.sleep(2)
                    return True
            except:
                continue
        return False
    except:
        return False

async def handle_buster(page):
    send_tg("🕵️ البحث عن الشخص الأصفر...")
    try:
        await asyncio.sleep(5)
        challenge_frame = page.frame_locator('iframe[title*="challenge"], iframe[src*="api2/bframe"]').first
        buster_btn = challenge_frame.locator("#solver-button")
        
        await buster_btn.wait_for(state="visible", timeout=20000)
        await buster_btn.click(force=True)
        send_tg("🎯 تم الضغط على الشخص الأصفر!")
        await asyncio.sleep(8)
        return True
    except Exception as e:
        send_tg(f"❌ الشخص الأصفر لم يظهر: {str(e)[:100]}")
        return False
# ==========================================

async def run():
    send_tg("🚀 بدء المهمة...")
    ext_path = await setup_buster()
    if not ext_path:
        send_tg("❌ فشل إعداد الإضافة")
        return
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            "/tmp/chrome_user_data",
            headless=False,
            proxy=WORKING_PROXY,
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--headless=new",
                "--no-sandbox"
            ]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        try:
            await context.add_cookies(MY_COOKIES)
            
            # تصوير صفحة الإضافات للتأكد من الحالة (ستراها ممتلئة هذه المرة)
            await page.goto("chrome://extensions/")
            await asyncio.sleep(3)
            await page.screenshot(path="verify.png")
            send_tg("📸 حالة الإضافة (الآن يفترض أن تظهر):", "verify.png")
            
            await page.goto(LAB_URL, timeout=60000)
            if await click_start_lab_button(page):
                await asyncio.sleep(5)
                if await click_captcha_checkbox(page):
                    await asyncio.sleep(4)
                    await handle_buster(page)
                    await asyncio.sleep(5)
                    await page.screenshot(path="final.png", full_page=True)
                    send_tg("📸 النتيجة:", "final.png")
                else:
                    await page.screenshot(path="captcha_fail.png", full_page=True)
                    send_tg("❌ فشل العثور على الكابتشا:", "captcha_fail.png")
            else:
                send_tg("❌ لم يتم العثور على زر Start Lab")
        except Exception as e: 
            send_tg(f"❌ خطأ: {e}")
        finally: 
            await context.close()

if __name__ == "__main__":
    asyncio.run(run())
