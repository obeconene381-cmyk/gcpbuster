import asyncio
import os
import zipfile
import requests
import re
import tempfile
from playwright.async_api import async_playwright

# ========== إعدادات التيليجرام ==========
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
# =====================================

BASE_URL = "https://www.skills.google/"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

# الكوكيز المُحدثة (تأكد أن القيمة المنسوخة صحيحة دائماً)
MY_COOKIES = [
    {"domain": ".google.com", "name": "__Secure-1PSID", "value": "g.a0008Ai6P4D9VxUMsensK1KpzeOc24d8VoHzO9H99BWH0mlOD6cmjs-BEg_YPf-HLWwDZdCefAACgYKAUISARMSFQHGX2MiwOJS0q3XWAy99YYvXGhGkhoVAUF8yKqoLEMDT5_IcXJDsfEymmDD0076", "path": "/", "secure": True},
    {"domain": ".google.com", "name": "__Secure-3PSID", "value": "g.a0008Ai6P4D9VxUMsensK1KpzeOc24d8VoHzO9H99BWH0mlOD6cmKA7Vb--6_FUasiorXlEHzwACgYKAQ4SARMSFQHGX2MiBsvg0VZbiwoRKrmJdnrlXBoVAUF8yKo5RslT3ogoQDVliD4Ua80o0076", "path": "/", "secure": True},
    {"domain": ".google.com", "name": "SID", "value": "g.a0008Ai6P4D9VxUMsensK1KpzeOc24d8VoHzO9H99BWH0mlOD6cmNAANXYlzTcpqDF3cHOeo4QACgYKAYgSARMSFQHGX2Miq4Sr8_RQAGM1RfiQnRkGtBoVAUF8yKrEeAB845ZqHKZcEyLv2YO20076", "path": "/"},
    {"domain": ".google.com", "name": "HSID", "value": "AMy4_Ta2HCzvZSQE3", "path": "/"},
    {"domain": ".google.com", "name": "SSID", "value": "Adb8GZVQq7ZbRgy9X", "path": "/", "secure": True},
    {"domain": ".google.com", "name": "SAPISID", "value": "UuI95bhHmuJTfRbY/AdsqK54C5qNUrOhdv", "path": "/", "secure": True},
    {"domain": ".skills.google", "name": "_ga", "value": "GA1.1.1438878037.1772447126", "path": "/"},
    {"domain": ".skills.google", "name": "_ga_2X30ZRBDSG", "value": "GS2.1.s1775996404$o97$g1$t1775996563$j32$l0$h0", "path": "/"},
    {"domain": "www.skills.google", "name": "_cvl-4_1_14_session", "value": "lQa%2FMnKdErx31nYRawt27XpphO7RO1Mod3%2FCk8T6PqZfkPZohBUhjBqhs2Mw1GIO229gr0KDHGkAp%2F9o7Blffpj%2BNy7YVlSwMKrQX3%2B0RxdyBzB0LU%2BFdcq5wLCPFWUPMhJNMngGjgVjse8JNXc1BO1j2FUpFQqvzAVGdPUShDJMshUZOva39naRS%2BVT%2BpBdaPE0I%2FgjsG6fC6KFeGqADXbUOQ36JiZQkoXYIjuKCxrOKwyaLKj7fFRebXiBduQKQIH3JK8bvcn0LkvK8BuvZ262zjAku4%2FkzRdFKfsfQMXrZStwGytxy1dqm%2FoQ6Lut8s9fnFVTGGcYIoJoxwba0Yx653S2FCemxd3GSCCqfGuNfuzRfNSCjsYvAeUmPdkQzepE80F3hbK15UUyM%2B2Puh3e4e%2FoovbnYf0xLZFGrxSpTcgJ5zb1FElGZ9LNFypWppJjbPlIySkS6X00pjko3fzmpi2TmUHvdBfPbn7ZmJbQ%2Fa8mQzvispzCN8GaAavsOZ%2FsD6xOt0%2FukYWX4oyXfRQg8AP8iZvYkj1iOvsbagPMKjp7utfL9DzDJ5n7LorhayjfSh9XLi1us38cm%2Fu8fzdbvLJn0DJ7koAN2V8V2KKLiGrU2H3e2z4pAFvTAmFENKac3LdIOOs2oNNj2Z8yF0iEnprV%2FzPeOb7eCcvFU66A6qb3f4SgUOTFVchEXizCrTx0%2FvdEQhoQG%2Boc3WXvnYtDbpPIuyt0BJSUda0e63hfWvQnww7DjHcdLtchLMoGYyOW0UktBRGkG3s%3D--TF35bd8CfnDqO%2BYr--Bp220SPOMrUj1y6NmvAiVw%3D%3D", "path": "/", "secure": True, "httpOnly": True},
    {"domain": "www.skills.google", "name": "user.id", "value": "eyJfcmFpbHMiOnsibWVzc2FnZSI6Ik1UTTNOVE13TmpJMyIsImV4cCI6bnVsbCwicHVyIjoiY29va2llLnVzZXIuaWQifX0%3D--3706d9f3abb091776145342b4e9be6e645941d44", "path": "/", "secure": True},
]

def send_tg(msg, img=None):
    if not BOT_TOKEN: return
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

async def click_button_smart(page, button_texts, timeout_loop=30):
    for text in button_texts:
        pattern = re.compile(re.escape(text), re.IGNORECASE)
        for _ in range(timeout_loop):
            for frame in [page] + page.frames:
                try:
                    locs = [
                        frame.get_by_role("button", name=pattern),
                        frame.locator(f"button:has-text('{text}')"),
                        frame.locator(f"[role='button']:has-text('{text}')")
                    ]
                    for loc in locators:
                        if await loc.count() > 0 and await loc.first.is_visible():
                            await loc.first.scroll_into_view_if_needed()
                            await loc.first.click(force=True, timeout=5000)
                            return True
                except: continue
            await asyncio.sleep(1)
    return False

async def solve_captcha(page):
    try:
        # البحث عن كابتشا وتفعيل Buster
        await page.wait_for_selector("iframe[src*='recaptcha']", timeout=10000)
        for frame in page.frames:
            if "api2/anchor" in frame.url:
                await frame.click(".recaptcha-checkbox-border", timeout=5000)
                await asyncio.sleep(3)
            if "api2/bframe" in frame.url:
                send_tg("🤖 جاري حل الكابتشا بواسطة Buster...")
                await frame.locator("#solver-button").click()
                await asyncio.sleep(12)
                return True
    except: pass
    return False

async def run():
    send_tg("⚙️ بدء تنفيذ الأتمتة...")
    ext_path = await get_ext()
    
    async with async_playwright() as p:
        # تشغيل المتصفح مع إخفاء بصمة الأتمتة
        browser = await p.chromium.launch(
            headless=True,
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox",
                "--disable-gpu",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        )
        
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()
        
        try:
            # الدخول لصفحة اللاب
            await page.goto(LAB_URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
            
            # محاولة بدء اللاب
            send_tg("🔍 جاري البحث عن زر بدء المختبر...")
            clicked = await click_button_smart(page, ["Start Lab", "بدء"], timeout_loop=30)
            
            if clicked:
                send_tg("✅ تم النقر على زر البدء.")
                await asyncio.sleep(5)
                await solve_captcha(page)
                await asyncio.sleep(15)
            else:
                send_tg("⚠️ لم يتم العثور على زر البدء (تأكد من صلاحية الكوكيز).")
            
            await page.screenshot(path="final.png")
            send_tg(f"🏁 انتهت العملية. الرابط الحالي:\n{page.url}", "final.png")
            
        except Exception as e:
            send_tg(f"❌ خطأ: {str(e)[:150]}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
