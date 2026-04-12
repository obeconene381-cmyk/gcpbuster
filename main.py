import asyncio
import os
import zipfile
import requests
import re
import json
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
        print(f"Telegram error: {e}")

async def get_ext():
    dest = os.path.abspath("ext_folder")
    zip_path = "buster.zip"
    
    # إذا لم يكن الملف موجوداً، نحاول تحميله
    if not os.path.exists(zip_path):
        send_tg("⏳ تحميل Buster...")
        try:
            url = "https://github.com/dessant/buster/archive/refs/heads/main.zip"
            r = requests.get(url, timeout=60)
            with open(zip_path, "wb") as f:
                f.write(r.content)
            send_tg("✅ تم تحميل Buster")
        except Exception as e:
            send_tg(f"❌ فشل التحميل: {e}")
            return None
    
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(dest)
        for r, d, f in os.walk(dest):
            if "manifest.json" in f:
                return os.path.abspath(r)
    return dest

async def click_start_lab_button(page):
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)
    for i in range(30): 
        try:
            # البحث في الصفحة الرئيسية فقط أولاً
            btns = page.get_by_role("button", name=pattern)
            if await btns.count() > 0:
                b = btns.first
                if await b.is_visible():
                    await b.click(force=True)
                    send_tg("✅ تم النقر على Start Lab")
                    return True
        except:
            pass
        
        # البحث في الـ iframes
        for frame in page.frames:
            try:
                btns = frame.get_by_role("button", name=pattern)
                if await btns.count() > 0:
                    b = btns.first
                    if await b.is_visible():
                        await b.click(force=True)
                        send_tg("✅ تم النقر على Start Lab (داخل iframe)")
                        return True
            except:
                continue
        
        await asyncio.sleep(1)
    return False

async def click_captcha_checkbox(page):
    send_tg("🔍 البحث عن مربع الكابتشا...")
    try:
        await asyncio.sleep(2)
        iframes = await page.locator('iframe[title*="reCAPTCHA"], iframe[src*="recaptcha"]').all()
        
        for iframe in iframes:
            try:
                frame_content = await iframe.content_frame()
                if frame_content:
                    checkbox = frame_content.locator('.recaptcha-checkbox-border').first
                    if await checkbox.count() > 0 and await checkbox.is_visible():
                        await checkbox.click(force=True)
                        send_tg("✅ تم الضغط على مربع الكابتشا")
                        await asyncio.sleep(2)
                        return True
            except:
                continue
        
        # محاولة ثانية بالـ JS
        try:
            await page.evaluate('''
                const checkbox = document.querySelector('.recaptcha-checkbox-border');
                if (checkbox) checkbox.click();
            ''')
            send_tg("✅ تم الضغط على المربع (JS)")
            return True
        except:
            pass
            
        return False
    except Exception as e:
        send_tg(f"❌ خطأ الكابتشا: {str(e)[:100]}")
        return False

async def handle_buster(page):
    send_tg("🕵️ البحث عن زر Buster...")
    try:
        # انتظار ظهور تحدي الصور
        await asyncio.sleep(3)
        
        challenge_frame = page.frame_locator('iframe[src*="api2/bframe"], iframe[title*="challenge"]').first
        buster_btn = challenge_frame.locator("#solver-button")
        
        await buster_btn.wait_for(state="visible", timeout=15000)
        await buster_btn.click(force=True)
        send_tg("🎯 تم الضغط على Buster!")
        
        # انتظار الحل (6 ثوانٍ كما طلبت)
        await asyncio.sleep(6)
        return True
        
    except Exception as e:
        send_tg(f"⚠️ Buster غير متوفر: {str(e)[:100]}")
        return False

async def click_launch_credits(page):
    try:
        pattern = re.compile(r"Launch\s*with\s*(\d+\s*)?Credits?", re.IGNORECASE)
        btn = page.get_by_role("button", name=pattern)
        
        if await btn.count() > 0:
            await btn.first.click(force=True)
            send_tg("🚀 تم الضغط على Launch Credits")
            await asyncio.sleep(3)
            return True
    except:
        pass
    return False

async def run():
    send_tg("🚀 بدء التشغيل...")
    ext_path = await get_ext()
    
    if not ext_path or not os.path.exists(ext_path):
        send_tg("❌ ملف Buster غير موجود")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            proxy=WORKING_PROXY,
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )

        context = await browser.new_context(
            proxy=WORKING_PROXY,
            viewport={'width': 1280, 'height': 720}
        )
        
        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()

        try:
            send_tg("🌐 فتح اللاب...")
            await page.goto(LAB_URL, timeout=90000, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=30000)

            # 1. الضغط على Start Lab
            if not await click_start_lab_button(page):
                send_tg("❌ لم يتم العثور على زر Start Lab")
                await page.screenshot(path="error_start.png", full_page=True)
                send_tg("📸:", "error_start.png")
                return

            await asyncio.sleep(3)

            # 2. الضغط على الكابتشا
            captcha_ok = await click_captcha_checkbox(page)
            
            if captcha_ok:
                await asyncio.sleep(3)
                
                # 3. محاولة Buster
                await handle_buster(page)
                
                # 4. الضغط على Launch إذا ظهر
                await click_launch_credits(page)
            
            # 5. النتيجة النهائية
            await asyncio.sleep(2)
            await page.screenshot(path="final_result.png", full_page=True)
            send_tg("📸 النتيجة النهائية:", "final_result.png")

        except Exception as e:
            send_tg(f"❌ خطأ: {str(e)[:200]}")
            try:
                await page.screenshot(path="error.png", full_page=True)
                send_tg("📸 خطأ:", "error.png")
            except:
                pass
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
