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

# مانيفست معدل لضمان القبول الفوري (بدون متغيرات لغوية معقدة في البداية)
CHROME_MANIFEST_CONTENT = {
    "manifest_version": 3,
    "name": "Buster Captcha Solver",
    "version": "1.0.0",
    "description": "Solving captchas for humans",
    "permissions": ["storage", "offscreen", "scripting"],
    "host_permissions": ["*://*.google.com/recaptcha/*", "*://*.recaptcha.net/*"],
    "background": {"service_worker": "src/background/script.js"},
    "content_scripts": [{
        "matches": ["*://*.google.com/recaptcha/*", "*://*.recaptcha.net/*"],
        "js": ["src/base/script.js"],
        "css": ["src/base/style.css"],
        "all_frames": True
    }],
    "icons": {"128": "src/assets/icons/app/icon-128.png"},
    "web_accessible_resources": [{"resources": ["src/base/solver-button.css"], "matches": ["<all_urls>"]}]
}

MY_COOKIES = [
    {"domain": ".skills.google", "name": "_ga", "value": "GA1.1.1438878037.1772447126", "path": "/"},
    {"domain": "www.skills.google", "name": "_cvl-4_1_14_session", "value": "lQa%2FMnKdErx31nYRawt27XpphO7RO1Mod3%2FCk8T6PqZfkPZohBUhjBqhs2Mw1GIO229gr0KDHGkAp%2F9o7Blffpj%2BNy7YVlSwMKrQX3%2B0RxdyBzB0LU%2BFdcq5wLCPFWUPMhJNMngGjgVjse8JNXc1BO1j2FUpFQqvzAVGdPUShDJMshUZOva39naRS%2BVT%2BpBdaPE0I%2FgjsG6fC6KFeGqADXbUOQ36JiZQkoXYIjuKCxrOKwyaLKj7fFRebXiBduQKQIH3JK8bvcn0LkvK8BuvZ262zjAku4%2FkzRdFKfsfQMXrZStwGytxy1dqm%2FoQ6Lut8s9fnFVTGGcYIoJoxwba0Yx653S2FCemxd3GSCCqfGuNfuzRfNSCjsYvAeUmPdkQzepE80F3hbK15UUyM%2B2Puh3e4e%2FoovbnYf0xLZFGrxSpTcgJ5zb1FElGZ9LNFypWppJjbPlIySkS6X00pjko3fzmpi2TmUHvdBfPbn7ZmJbQ%2Fa8mQzvispzCN8GaAavsOZ%2FsD6xOt0%2FukYWX4oyXfRQg8AP8iZvYkj1iOvsbagPMKjp7utfL9DzDJ5n7LorhayjfSh9XLi1us38cm%2Fu8fzdbvLJn0DJ7koAN2V8V2KKLiGrU2H3e2z4pAFvTAmFENKac3LdIOOs2oNNj2Z8yF0iEnprV%2FzPeOb7eCcvFU66A6qb3f4SgUOTFVchEXizCrTx0%2FvdEQhoQG%2Boc3WXvnYtDbpPIuyt0BJSUda0e63hfWvQnww7DjHcdLtchLMoGYyOW0UktBRGkG3s%3D--TF35bd8CfnDqO%2BYr--Bp220SPOMrUj1y6NmvAiVw%3D%3D", "path": "/", "secure": True, "httpOnly": True},
]

def send_tg(msg, img=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if img and os.path.exists(img):
            with open(img, "rb") as f: requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": msg}, files={"photo": f}, timeout=30)
        else: requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": msg}, timeout=30)
    except: print(f"Failed to send TG: {msg}")

async def setup_diagnostic_buster():
    """إعداد الإضافة مع تنظيف كامل للمجلدات لضمان عدم حدوث تداخل"""
    ext_dir = os.path.abspath("buster_final_ext")
    if os.path.exists(ext_dir): shutil.rmtree(ext_dir)
    os.makedirs(ext_dir)
    
    try:
        send_tg("⚙️ جاري محاولة بناء الإضافة برمجياً...")
        r = requests.get(BUSTER_ZIP_URL)
        with open("temp.zip", "wb") as f: f.write(r.content)
        
        with zipfile.ZipFile("temp.zip", 'r') as z: z.extractall("temp_raw")
        
        # العثور على مجلد src
        raw_folder = next(iter(os.listdir("temp_raw")))
        src_path = os.path.join("temp_raw", raw_folder, "src")
        
        # نقل المحتويات
        shutil.move(src_path, os.path.join(ext_dir, "src"))
        
        # كتابة المانيفست
        with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
            json.dump(CHROME_MANIFEST_CONTENT, f, indent=2)
            
        shutil.rmtree("temp_raw")
        os.remove("temp.zip")
        return ext_dir
    except Exception as e:
        send_tg(f"❌ فشل الإعداد البرمجي: {e}")
        return None

# --- دوال الضغط (أصلية 100% كما في كودك الناجح) ---
async def human_click(page, locator):
    try:
        await locator.scroll_into_view_if_needed()
        box = await locator.bounding_box()
        if box:
            x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            await page.mouse.move(x, y, steps=10)
            await asyncio.sleep(0.2)
            await page.mouse.down()
            await asyncio.sleep(0.15)
            await page.mouse.up()
            return True
        await locator.click(delay=200)
        return True
    except: return False

async def click_start_lab_button(page):
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)
    for _ in range(30):
        try:
            btn = page.get_by_role("button", name=pattern).first
            if await btn.is_visible():
                await btn.click(force=True)
                send_tg("✅ تم الضغط على Start Lab")
                return True
        except: pass
        await asyncio.sleep(1)
    return False

async def run():
    send_tg("🚀 بدء المهمة التشخيصية...")
    ext_path = await setup_diagnostic_buster()
    if not ext_path: return

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            "/tmp/chrome_diag",
            headless=False,
            args=[f"--disable-extensions-except={ext_path}", f"--load-extension={ext_path}", "--headless=new", "--no-sandbox"],
            proxy=WORKING_PROXY
        )
        page = context.pages[0]
        try:
            await context.add_cookies(MY_COOKIES)
            
            # --- خطوة التشخيص 1: فحص الإضافات ---
            send_tg("🔍 فحص حقن الإضافة...")
            await page.goto("chrome://extensions/")
            await asyncio.sleep(3)
            await page.screenshot(path="diag_extensions.png")
            send_tg("📸 صورة لصفحة الإضافات:", "diag_extensions.png")
            
            # فحص إذا كان هناك زر "Errors"
            if await page.get_by_role("button", name="Errors").count() > 0:
                await page.get_by_role("button", name="Errors").first.click()
                await asyncio.sleep(1)
                await page.screenshot(path="ext_errors.png")
                send_tg("⚠️ تم اكتشاف أخطاء في الإضافة! إليك التفاصيل:", "ext_errors.png")

            # --- خطوة التشخيص 2: الدخول للاب ---
            await page.goto(LAB_URL, timeout=60000)
            await page.screenshot(path="diag_lab_page.png")
            send_tg("🌐 صفحة اللاب محملة:", "diag_lab_page.png")
            
            if await click_start_lab_button(page):
                await asyncio.sleep(5)
                await page.screenshot(path="diag_after_start.png")
                send_tg("📸 ما بعد الضغط على Start Lab:", "diag_after_start.png")
                
                # البحث عن الكابتشا
                iframes = await page.locator('iframe[title*="reCAPTCHA"]').all()
                if not iframes:
                    send_tg("❌ لم يتم العثور على أي iframe للكابتشا!")
                else:
                    send_tg(f"✅ تم العثور على {len(iframes)} إطار كابتشا.")
                    # محاولة الضغط
                    for iframe in iframes:
                        frame = iframe.content_frame
                        checkbox = frame.locator('.recaptcha-checkbox-border').first
                        if await checkbox.is_visible():
                            await human_click(page, checkbox)
                            send_tg("✅ تم الضغط على المربع.")
                            
                            # التشخيص 3: هل ظهر Buster؟
                            await asyncio.sleep(5)
                            challenge_frame = page.frame_locator('iframe[title*="challenge"]').first
                            await page.screenshot(path="diag_buster_check.png")
                            if await challenge_frame.locator("#solver-button").is_visible():
                                send_tg("🎯 زر Buster ظهر بنجاح!", "diag_buster_check.png")
                                await challenge_frame.locator("#solver-button").click()
                            else:
                                send_tg("❌ زر Buster لم يظهر داخل التحدي.", "diag_buster_check.png")
            
            await asyncio.sleep(5)
            await page.screenshot(path="final_diag.png")
            send_tg("📸 الحالة النهائية للمهمة:", "final_diag.png")

        except Exception as e:
            send_tg(f"🔥 خطأ غير متوقع: {e}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run())
