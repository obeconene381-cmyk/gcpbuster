import asyncio
import os
import zipfile
import requests
import re
from playwright.async_api import async_playwright

BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

# إعدادات البروكسي الشغال (تم حذف استرو)
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
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": msg}, files={"photo": f}, timeout=20)
        else:
            requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": msg}, timeout=20)
    except: pass

async def get_ext():
    dest = "ext_folder"
    if os.path.exists("buster-main.zip"):
        with zipfile.ZipFile("buster-main.zip", 'r') as z:
            z.extractall(dest)
        for r, d, f in os.walk(dest):
            if "manifest.json" in f: return os.path.abspath(r)
    return os.path.abspath(dest)

# --- دالة الضغط على Start Lab ---
async def click_start_lab_button(page):
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)
    for _ in range(60): # محاولة لمدة دقيقة
        for target in [page] + list(page.frames):
            try:
                btns = target.get_by_role("button", name=pattern)
                if await btns.count() > 0:
                    b = btns.first
                    if await b.is_visible():
                        await b.click(force=True)
                        send_tg("✅ تم النقر على Start Lab")
                        return True
            except: continue
        await asyncio.sleep(1)
    return False

# --- دالة الضغط على الكابتشا ---
async def click_captcha_checkbox(page):
    send_tg("🤛 جاري البحث عن مربع الكابتشا...")
    try:
        await asyncio.sleep(3)
        iframes = await page.locator('iframe').all()
        for iframe in iframes:
            frame_content = iframe.content_frame
            checkbox = frame_content.locator('.recaptcha-checkbox-border').first
            if await checkbox.count() > 0:
                await checkbox.click(force=True, delay=150)
                send_tg("✅ تم الضغط على المربع بنجاح")
                await asyncio.sleep(2)
                await page.screenshot(path="after_click.png", full_page=True)
                send_tg("📸 حالة الكابتشا بعد الضغط:", "after_click.png")
                return True
        send_tg("❌ لم يتم العثور على المربع.")
        return False
    except: return False

# --- دالة Buster ---
async def handle_buster(page):
    try:
        challenge_frame = page.frame_locator('iframe[src*="api2/bframe"]').first
        audio_btn = challenge_frame.locator("#recaptcha-audio-button")
        await audio_btn.wait_for(state="visible", timeout=10000)
        await audio_btn.click()
        await asyncio.sleep(2)
        buster_btn = challenge_frame.locator("#solver-button")
        await buster_btn.click()
        send_tg("🎯 تم تفعيل Buster لحل التحدي")
        await asyncio.sleep(10)
    except: pass

async def run():
    ext_path = await get_ext()
    async with async_playwright() as p:
        # الحقن في launch
        browser = await p.chromium.launch(
            headless=True,
            proxy=WORKING_PROXY, 
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        # التأكيد على الحقن في context أيضاً لضمان عدم التسريب
        context = await browser.new_context(proxy=WORKING_PROXY)
        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()

        try:
            send_tg("🌐 جاري محاولة فتح الصفحة بالبروكسي الجديد...")
            # استخدمنا wait_until="commit" ليكون أسرع ولا يتوقف عند ملفات التتبع
            await page.goto(LAB_URL, timeout=90000, wait_until="commit")
            
            # انتظر يدوياً ظهور شيء في الصفحة للتأكد
            await page.wait_for_load_state("domcontentloaded", timeout=30000)
            
            await page.screenshot(path="loaded.png")
            send_tg("📸 تم تحميل الصفحة بنجاح", "loaded.png")

            if await click_start_lab_button(page):
                await asyncio.sleep(5)
                await click_captcha_checkbox(page)
                await handle_buster(page)
                
                await asyncio.sleep(5)
                await page.screenshot(path="final.png")
                send_tg("🏁 انتهت المهمة", "final.png")
            else:
                send_tg("❌ لم أجد زر Start Lab")

        except Exception as e:
            send_tg(f"❌ خطأ: {str(e)[:100]}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
