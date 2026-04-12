import asyncio
import os
import zipfile
import requests
import re
import tempfile
from playwright.async_api import async_playwright

# إعدادات التيليجرام
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"

BASE_URL = "https://www.skills.google/"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

MY_COOKIES = [
    {"domain": ".skills.google", "name": "_ga", "value": "GA1.1.1438878037.1772447126", "path": "/"},
    {"domain": ".skills.google", "name": "_ga_2X30ZRBDSG", "value": "GS2.1.s1775996404$o97$g1$t1775996563$j32$l0$h0", "path": "/"},
    {"domain": "www.skills.google", "name": "_cvl-4_1_14_session", "value": "lQa%2FMnKdErx31nYRawt27XpphO7RO1Mod3%2FCk8T6PqZfkPZohBUhjBqhs2Mw1GIO229gr0KDHGkAp%2F9o7Blffpj%2BNy7YVlSwMKrQX3%2B0RxdyBzB0LU%2BFdcq5wLCPFWUPMhJNMngGjgVjse8JNXc1BO1j2FUpFQqvzAVGdPUShDJMshUZOva39naRS%2BVT%2BpBdaPE0I%2FgjsG6fC6KFeGqADXbUOQ36JiZQkoXYIjuKCxrOKwyaLKj7fFRebXiBduQKQIH3JK8bvcn0LkvK8BuvZ262zjAku4%2FkzRdFKfsfQMXrZStwGytxy1dqm%2FoQ6Lut8s9fnFVTGGcYIoJoxwba0Yx653S2FCemxd3GSCCqfGuNfuzRfNSCjsYvAeUmPdkQzepE80F3hbK15UUyM%2B2Puh3e4e%2FoovbnYf0xLZFGrxSpTcgJ5zb1FElGZ9LNFypWppJjbPlIySkS6X00pjko3fzmpi2TmUHvdBfPbn7ZmJbQ%2Fa8mQzvispzCN8GaAavsOZ%2FsD6xOt0%2FukYWX4oyXfRQg8AP8iZvYkj1iOvsbagPMKjp7utfL9DzDJ5n7LorhayjfSh9XLi1us38cm%2Fu8fzdbvLJn0DJ7koAN2V8V2KKLiGrU2H3e2z4pAFvTAmFENKac3LdIOOs2oNNj2Z8yF0iEnprV%2FzPeOb7eCcvFU66A6qb3f4SgUOTFVchEXizCrTx0%2FvdEQhoQG%2Boc3WXvnYtDbpPIuyt0BJSUda0e63hfWvQnww7DjHcdLtchLMoGYyOW0UktBRGkG3s%3D--TF35bd8CfnDqO%2BYr--Bp220SPOMrUj1y6NmvAiVw%3D%3D", "path": "/", "secure": True, "httpOnly": True},
    {"domain": "www.skills.google", "name": "browser.timezone", "value": "Africa/Algiers", "path": "/"},
    {"domain": "www.skills.google", "name": "user.expires_at", "value": "eyJfcmFpbHMiOnsibWVzc2FnZSI6IklqSXdNall0TURRdE1USlVNVEE2TWpJNk5EQXVPVFF5TFRBME9qQXdJZz09IiwiZXhwIjpudWxsLCJwdXIiOiJjb29raWUudXNlci5leHBpcmVzX2F0In19--4e4003b1ef46679dd053dc0a5fa9e9f1ee8b1798", "path": "/", "secure": True},
    {"domain": "www.skills.google", "name": "user.id", "value": "eyJfcmFpbHMiOnsibWVzc2FnZSI6Ik1UTTNOVE13TmpJMyIsImV4cCI6bnVsbCwicHVyIjoiY29va2llLnVzZXIuaWQifX0%3D--3706d9f3abb091776145342b4e9be6e645941d44", "path": "/", "secure": True}
]

def send_tg(msg, img=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if img and os.path.exists(img):
            with open(img, "rb") as f:
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": msg}, files={"photo": f}, timeout=20)
        else:
            requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": msg}, timeout=20)
    except: pass

async def get_ext():
    zip_p = "buster-main.zip"
    dest = "ext_folder"
    if os.path.exists(zip_p):
        with zipfile.ZipFile(zip_p, 'r') as z: z.extractall(dest)
        for r, d, f in os.walk(dest):
            if "manifest.json" in f: return os.path.abspath(r)
    return os.path.abspath(dest)

async def run():
    send_tg("⚙️ جاري بدء المهمة وإعداد الصور...")
    ext_path = await get_ext()
    temp_dir = tempfile.mkdtemp()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()

        try:
            await page.goto(BASE_URL, wait_until="networkidle")
            await asyncio.sleep(4)
            await page.goto(LAB_URL, wait_until="networkidle")
            await asyncio.sleep(6)
            
            # صورة 1: صفحة اللاب عند الدخول
            await page.screenshot(path="step1.png")
            send_tg("📸 1. تم فتح صفحة اللاب بنجاح.", "step1.png")

            # محاولة النقر على الزر بمحددات متعددة
            send_tg("🔍 جاري البحث عن زر Start Lab...")
            
            # قائمة المحددات (Selectors) الأكثر دقة
            selectors = ["button.ql-button", "button:has-text('Start Lab')", ".js-start-lab-button"]
            clicked = False
            
            for selector in selectors:
                for target in [page] + page.frames:
                    try:
                        btn = target.locator(selector).first
                        if await btn.is_visible():
                            await btn.click(force=True)
                            clicked = True
                            break
                    except: continue
                if clicked: break

            if clicked:
                send_tg("✅ تم العثور على الزر والضغط عليه.")
                await asyncio.sleep(5)
                
                # صورة 2: بعد الضغط (هل ظهرت الكبتشا؟)
                await page.screenshot(path="after_click.png")
                send_tg("📸 2. الحالة بعد الضغط على الزر.", "after_click.png")

                # حل الكبتشا
                for f in page.frames:
                    if "api2/anchor" in f.url:
                        await f.click(".recaptcha-checkbox-border")
                        await asyncio.sleep(3)
                    if "api2/bframe" in f.url:
                        send_tg("🤖 تم اكتشاف الكبتشا، جاري الحل...")
                        await f.locator("#solver-button").click()
                        await asyncio.sleep(15)
            else:
                await page.screenshot(path="failed.png")
                send_tg("❌ لم أتمكن من العثور على الزر برمجياً رغم وجوده في الصورة.", "failed.png")

            await asyncio.sleep(10)
            await page.screenshot(path="final.png")
            send_tg(f"🏁 المهمة انتهت. الرابط الحالي:\n{page.url}", "final.png")

        except Exception as e:
            send_tg(f"❌ خطأ: {str(e)[:200]}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
