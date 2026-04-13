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

# 🔥 التعديل الجوهري: استخدام النسخة المبنية والجاهزة للكروم من إصدارات المطور الرسمية 🔥
BUSTER_COMPILED_URL = "https://github.com/dessant/buster/releases/download/v3.1.0/buster_captcha_solver_for_humans-3.1.0-chrome.zip"

WORKING_PROXY = {
    "server": "http://92.119.128.15:9996",
    "username": "user376353",
    "password": "y3ld6w"
}

MY_COOKIES = [
    {"domain": ".skills.google", "name": "_ga", "value": "GA1.1.1438878037.1772447126", "path": "/"},
    {"domain": "www.skills.google", "name": "_cvl-4_1_14_session", "value": "lQa%2FMnKdErx31nYRawt27XpphO7RO1Mod3%2FCk8T6PqZfkPZohBUhjBqhs2Mw1GIO229gr0KDHGkAp%2F9o7Blffpj%2BNy7YVlSwMKrQX3%2B0RxdyBzB0LU%2BFdcq5wLCPFWUPMhJNMngGjgVjse8JNXc1BO1j2FUpFQqvzAVGdPUShDJMshUZOva39naRS%2BVT%2BpBdaPE0I%2FgjsG6fC6KFeGqADXbUOQ36JiZQkoXYIjuKCxrOKwyaLKj7fFRebXiBduQKQIH3JK8bvcn0LkvK8BuvZ262zjAku4%2FkzRdFKfsfQMXrZStwGytxy1dqm%2FoQ6Lut8s9fnFVTGGcYIoJoxwba0Yx653S2FCemxd3GSCCqfGuNfuzRfNSCjsYvAeUmPdkQzepE80F3hbK15UUyM%2B2Puh3e4e%2FoovbnYf0xLZFGrxSpTcgJ5zb1FElGZ9LNFypWppJjbPlIySkS6X00pjko3fzmpi2TmUHvdBfPbn7ZmJbQ%2Fa8mQzvispzCN8GaAavsOZ%2FsD6xOt0%2FukYWX4oyXfRQg8AP8iZvYkj1iOvsbagPMKjp7utfL9DzDJ5n7LorhayjfSh9XLi1us38cm%2Fu8fzdbvLJn0DJ7koAN2V8V2KKLiGrU2H3e2z4pAFvTAmFENKac3LdIOOs2oNNj2Z8yF0iEnprV%2FzPeOb7eCcvFU66A6qb3f4SgUOTFVchEXizCrTx0%2FvdEQhoQG%2Boc3WXvnYtDbpPIuyt0BJSUda0e63hfWvQnww7DjHcdLtchLMoGYyOW0UktBRGkG3s%3D--TF35bd8CfnDqO%2BYr--Bp220SPOMrUj1y6NmvAiVw%3D%3D", "path": "/", "secure": True, "httpOnly": True},
    {"domain": "www.skills.google", "name": "user.id", "value": "eyJfcmFpbHMiOnsibWVzc2FnZSI6Ik1UTTNOVE13TmpJMyIsImV4cCI6bnVsbCwicHVyIjoiY29va2llLnVzZXIuaWQifX0%3D--3706d9f3abb091776145342b4e9be6e645941d44", "path": "/", "secure": True},
]

def send_tg(msg, img=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if img and os.path.exists(img):
            with open(img, "rb") as f: requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": msg}, files={"photo": f}, timeout=30)
        else: requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": msg}, timeout=30)
    except: pass

async def setup_compiled_buster():
    """تحميل النسخة الجاهزة من الإضافة لضمان عملها الفوري دون تعديل برمجي منا"""
    ext_dir = os.path.abspath("buster_compiled_ext")
    if os.path.exists(ext_dir): shutil.rmtree(ext_dir)
    os.makedirs(ext_dir)
    zip_path = "buster_ready.zip"
    
    try:
        send_tg("📥 جاري تحميل النسخة الرسمية الجاهزة للإضافة...")
        r = requests.get(BUSTER_COMPILED_URL, timeout=30)
        with open(zip_path, "wb") as f: f.write(r.content)
        
        # فك الضغط في المجلد مباشرة
        with zipfile.ZipFile(zip_path, 'r') as z: 
            z.extractall(ext_dir)
            
        os.remove(zip_path)
        send_tg(f"✅ تم تجهيز الإضافة الجاهزة في المسار: {ext_dir}")
        return ext_dir
    except Exception as e:
        send_tg(f"❌ فشل تحميل الإضافة الجاهزة: {e}")
        return None

# ===============================================
# دوالك الأصلية للضغط بقيت كما هي دون أي تغيير
# ===============================================
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

# --- الدالة الجديدة للتعامل مع النافذة المنبثقة للـ Credits ---
async def dismiss_credits_modal(page):
    try:
        # البحث عن زر "Dismiss" (تخطي النافذة إذا ظهرت)
        btn = page.get_by_role("button", name=re.compile(r"Dismiss", re.I))
        if await btn.count() > 0 and await btn.first.is_visible():
            await btn.first.click()
            send_tg("✅ تم العثور على نافذة Credits Expiring وإغلاقها.")
            await asyncio.sleep(2)
            return True
            
        # محاولة أخرى بالنص المباشر
        text_btn = page.locator("text=Dismiss")
        if await text_btn.count() > 0 and await text_btn.first.is_visible():
            await text_btn.first.click()
            send_tg("✅ تم إغلاق نافذة Credits Expiring.")
            await asyncio.sleep(2)
            return True
    except Exception as e:
        pass
    return False

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
    send_tg("🤛 البحث عن مربع الكابتشا...")
    await asyncio.sleep(3)
    iframes = await page.locator('iframe[title*="reCAPTCHA"]').all()
    for iframe in iframes:
        try:
            frame_content = iframe.content_frame
            checkbox = frame_content.locator('.recaptcha-checkbox-border').first
            if await checkbox.is_visible():
                await human_click(page, checkbox)
                send_tg("✅ تم الضغط على المربع")
                return True
        except: continue
    return False

async def handle_buster(page):
    send_tg("🕵️ البحث عن الشخص الأصفر...")
    try:
        await asyncio.sleep(5)
        challenge_frame = page.frame_locator('iframe[title*="challenge"]').first
        buster_btn = challenge_frame.locator("#solver-button")
        await buster_btn.wait_for(state="visible", timeout=15000)
        await buster_btn.click(force=True)
        send_tg("🎯 تم الضغط على الشخص الأصفر!")
        await asyncio.sleep(8)
        return True
    except: return False

# ===============================================

async def run():
    send_tg("🚀 بدء المهمة باستخدام النسخة الجاهزة من Buster...")
    ext_path = await setup_compiled_buster()
    if not ext_path: return

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            "/tmp/chrome_diag",
            headless=False,
            args=[f"--disable-extensions-except={ext_path}", f"--load-extension={ext_path}", "--headless=new", "--no-sandbox"],
            proxy=WORKING_PROXY,
            viewport={'width': 1280, 'height': 720}
        )
        page = context.pages[0]
        try:
            await context.add_cookies(MY_COOKIES)
            
            # 1. التأكد من الإضافة
            await page.goto("chrome://extensions/")
            await asyncio.sleep(2)
            await page.screenshot(path="diag_extensions.png")
            send_tg("📸 الإضافة الآن يجب أن تكون ظاهرة هنا:", "diag_extensions.png")
            
            # 2. الدخول للاب
            await page.goto(LAB_URL, timeout=60000)
            await asyncio.sleep(4)
            
            # 🔥 التعامل مع النافذة المنبثقة إن وجدت 🔥
            await dismiss_credits_modal(page)
            
            await page.screenshot(path="diag_lab_page.png")
            send_tg("🌐 صفحة اللاب بعد معالجة النوافذ:", "diag_lab_page.png")
            
            # 3. بدء اللاب واستكمال المهمة
            if await click_start_lab_button(page):
                await asyncio.sleep(5)
                await page.screenshot(path="diag_after_start.png")
                send_tg("📸 ما بعد الضغط على Start Lab:", "diag_after_start.png")
                
                if await click_captcha_checkbox(page):
                    await handle_buster(page)
                    await asyncio.sleep(5)
                    await page.screenshot(path="final_diag.png")
                    send_tg("📸 النتيجة النهائية:", "final_diag.png")
                else:
                    send_tg("❌ لم يظهر مربع الكابتشا")

        except Exception as e:
            send_tg(f"🔥 خطأ غير متوقع: {e}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run())
