import asyncio
import os
import zipfile
import requests
import re
import shutil
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
    """تحميل الإضافة وإصلاح هيكل الملفات لتعمل على متصفح كروم"""
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
        
        # البحث عن ملف chrome.json لتحويله إلى manifest.json
        chrome_json_path = None
        src_path = None
        for root, dirs, files in os.walk(target_dir):
            if "chrome.json" in files:
                chrome_json_path = os.path.join(root, "chrome.json")
            if "background.js" in files or "background" in dirs: # المجلد الذي يحتوي على الكود الفعلي
                src_path = root
                
        if chrome_json_path and src_path:
            # نسخ chrome.json إلى المجلد الرئيسي كـ manifest.json
            final_manifest = os.path.join(src_path, "manifest.json")
            shutil.copy(chrome_json_path, final_manifest)
            send_tg(f"🛠️ تم تحويل chrome.json إلى manifest.json في المسار: {src_path}")
            return os.path.abspath(src_path)
                
        return None
    except Exception as e:
        send_tg(f"❌ خطأ في الإعداد: {e}")
        return None

# --- دوال الضغط (لم يتم لمسها) ---
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

async def click_captcha_checkbox(page):
    send_tg("🤛 محاولة الضغط على مربع الكابتشا...")
    try:
        await asyncio.sleep(5)
        iframes = await page.locator('iframe[title*="reCAPTCHA"]').all()
        for iframe in iframes:
            frame = iframe.content_frame
            checkbox = frame.locator('.recaptcha-checkbox-border').first
            if await checkbox.is_visible():
                await human_click(page, checkbox)
                send_tg("✅ تم تفعيل المربع")
                return True
        return False
    except: return False

async def handle_buster(page):
    send_tg("🕵️ البحث عن أيقونة Buster...")
    try:
        await asyncio.sleep(5)
        challenge_frame = page.frame_locator('iframe[title*="challenge"], iframe[src*="api2/bframe"]').first
        buster_btn = challenge_frame.locator("#solver-button")
        await buster_btn.wait_for(state="visible", timeout=15000)
        await buster_btn.click()
        send_tg("🎯 تم تشغيل Buster!")
        return True
    except:
        send_tg("❌ لم تظهر الإضافة في الكابتشا")
        return False

async def run():
    send_tg("🚀 بدء المهمة...")
    ext_path = await setup_buster()
    if not ext_path:
        send_tg("❌ تعذر إيجاد ملفات الإضافة الضرورية")
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
        page = context.pages[0]
        try:
            await context.add_cookies(MY_COOKIES)
            
            # تصوير صفحة الإضافات للتأكد من الحالة
            await page.goto("chrome://extensions/")
            await asyncio.sleep(3)
            await page.screenshot(path="verify.png")
            send_tg("📸 حالة الإضافات بعد الإصلاح:", "verify.png")
            
            await page.goto(LAB_URL, timeout=60000)
            if await click_start_lab_button(page):
                if await click_captcha_checkbox(page):
                    await handle_buster(page)
                    await asyncio.sleep(5)
                    await page.screenshot(path="final.png")
                    send_tg("📸 النتيجة:", "final.png")
        except Exception as e: send_tg(f"❌ خطأ: {e}")
        finally: await context.close()

if __name__ == "__main__":
    asyncio.run(run())
