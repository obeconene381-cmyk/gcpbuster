import asyncio
import os
import zipfile
import requests
import re
from playwright.async_api import async_playwright

# --- الإعدادات ---
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

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
    except Exception as e:
        print(f"TG Error: {e}")

async def get_buster_path():
    """البحث الديناميكي عن مجلد Buster بالبحث عن ملف manifest.json"""
    for root, dirs, files in os.walk(os.getcwd()):
        if "manifest.json" in files:
            return os.path.abspath(root)
    return None

# --- دوال الضغط بقيت كما هي دون أي تعديل ---
async def human_click(page, locator):
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
# -----------------------------------------------

async def run():
    send_tg("🚀 بدء المهمة...")
    
    ext_path = await get_buster_path()
    if not ext_path:
        send_tg("❌ لم يتم العثور على ملفات إضافة Buster (لم يتم إيجاد manifest.json)")
        return
    
    send_tg(f"📂 تم إيجاد الإضافة بنجاح في: {ext_path}")
    
    async with async_playwright() as p:
        # ملاحظة هامة: يجب أن يكون headless=False مع استخدام --headless=new لتعمل الإضافات
        context = await p.chromium.launch_persistent_context(
            "/tmp/chrome_profile",
            headless=False,  # تم التعديل هنا لضمان عمل الإضافة
            proxy=WORKING_PROXY,
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--headless=new", # تفعيل وضع headless الداعم للإضافات
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage"
            ],
            viewport={'width': 1280, 'height': 720}
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        try:
            await context.add_cookies(MY_COOKIES)
            
            # --- التأكد من عمل الإضافة قبل الدخول للاب ---
            send_tg("🔍 جاري فحص صفحة الإضافات للتأكد من تحميل Buster...")
            await page.goto("chrome://extensions/")
            await asyncio.sleep(2)
            await page.screenshot(path="extensions_check.png", full_page=True)
            send_tg("📸 صورة لصفحة الإضافات للتأكد:", "extensions_check.png")
            # ----------------------------------------------
            
            send_tg("🌐 فتح اللاب...")
            await page.goto(LAB_URL, timeout=90000, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            await page.screenshot(path="lab_loaded.png", full_page=True)
            send_tg("📸 تم تحميل اللاب", "lab_loaded.png")

            if await click_start_lab_button(page):
                await asyncio.sleep(5)
                if await click_captcha_checkbox(page):
                    await asyncio.sleep(4)
                    await handle_buster(page)
                    
                    await asyncio.sleep(2)
                    await page.screenshot(path="final.png", full_page=True)
                    send_tg("📸 النتيجة:", "final.png")
                else:
                    await page.screenshot(path="captcha_fail.png", full_page=True)
                    send_tg("❌ فشل الكابتشا:", "captcha_fail.png")
            else:
                send_tg("❌ لم يتم العثور على Start Lab")

        except Exception as e:
            send_tg(f"❌ خطأ: {str(e)[:200]}")
            try:
                await page.screenshot(path="error.png", full_page=True)
                send_tg("📸 خطأ:", "error.png")
            except:
                pass
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run())
