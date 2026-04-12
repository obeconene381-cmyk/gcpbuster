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

# دمج كوكيز Google العامة مع كوكيز skills.google
MY_COOKIES = [
    # كوكيز skills.google
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
    except Exception as e:
        print(f"Telegram error: {e}")

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

async def find_and_click_start_lab(page):
    """بحث شامل عن زر Start Lab بكل الطرق الممكنة"""
    # قائمة موسعة من النصوص والمحددات
    text_variants = [
        "Start Lab", "START LAB", "Start lab",
        "بدء", "ابدأ", "بدء المختبر", "بدء المعمل",
        "Start", "بدء الآن"
    ]
    
    selectors = [
        "button:has-text('Start Lab')",
        "button:has-text('START LAB')",
        "button:has-text('بدء')",
        "a:has-text('Start Lab')",
        "a:has-text('بدء')",
        "[role='button']:has-text('Start Lab')",
        ".ql-button",
        ".start-lab-button",
        "[data-testid='start-lab-button']",
        "button[aria-label*='Start']",
        "button[aria-label*='بدء']",
        # محددات عامة
        "button",
        "a.button",
        ".btn-primary",
    ]

    # 1. البحث باستخدام النصوص
    for text in text_variants:
        for _ in range(5):  # محاولة لمدة 5 ثوان لكل نص
            for frame in [page] + page.frames:
                try:
                    locator = frame.get_by_text(text, exact=False).first
                    if await locator.count() > 0 and await locator.is_visible():
                        await locator.scroll_into_view_if_needed()
                        await locator.click(force=True, timeout=5000)
                        return True
                except:
                    pass
            await asyncio.sleep(1)

    # 2. البحث باستخدام المحددات
    for selector in selectors:
        try:
            for frame in [page] + page.frames:
                locs = frame.locator(selector)
                count = await locs.count()
                for i in range(count):
                    btn = locs.nth(i)
                    if await btn.is_visible() and await btn.is_enabled():
                        text_content = await btn.text_content() or ""
                        if any(keyword.lower() in text_content.lower() for keyword in ["start", "lab", "بدء"]):
                            await btn.scroll_into_view_if_needed()
                            await btn.click(force=True, timeout=5000)
                            return True
        except:
            continue

    # 3. استخدام JavaScript للنقر على أي زر يبدو مناسباً
    try:
        result = await page.evaluate("""
            () => {
                const buttons = [...document.querySelectorAll('button, a[role="button"], div[role="button"]')];
                const startBtn = buttons.find(btn => {
                    const text = btn.innerText.toLowerCase();
                    return text.includes('start lab') || text.includes('بدء') || text.includes('ابدأ');
                });
                if (startBtn) {
                    startBtn.scrollIntoView({behavior: 'smooth', block: 'center'});
                    startBtn.click();
                    return true;
                }
                return false;
            }
        """)
        if result:
            return True
    except:
        pass

    return False

async def solve_captcha(page):
    """معالجة reCAPTCHA"""
    try:
        await page.wait_for_selector("iframe[src*='recaptcha']", timeout=15000)
        for frame in page.frames:
            if "api2/anchor" in frame.url:
                await frame.click(".recaptcha-checkbox-border", timeout=5000)
                await asyncio.sleep(3)
            if "api2/bframe" in frame.url:
                send_tg("🤖 تحدي كابتشا، جاري استخدام Buster...")
                await frame.locator("#solver-button").click(timeout=10000)
                await asyncio.sleep(15)
                return True
    except:
        pass
    return False

async def run():
    send_tg("🚀 بدء المهمة...")
    ext_path = await get_ext()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled",
                "--window-size=1280,720"
            ]
        )
        
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()
        
        try:
            send_tg("🌐 فتح صفحة اللاب...")
            await page.goto(LAB_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)
            
            await page.screenshot(path="lab_page.png")
            send_tg("📸 صفحة اللاب مفتوحة", "lab_page.png")
            
            # محاولة النقر على Start Lab
            send_tg("🔍 البحث عن زر Start Lab...")
            clicked = await find_and_click_start_lab(page)
            
            if clicked:
                send_tg("✅ تم الضغط على زر البدء بنجاح")
                await asyncio.sleep(5)
                
                # معالجة الكابتشا
                await solve_captcha(page)
                
                await asyncio.sleep(10)
                await page.screenshot(path="after_click.png")
                send_tg("📸 بعد الضغط على البدء", "after_click.png")
            else:
                send_tg("⚠️ لم يتم العثور على زر البدء. ربما اللاب بدأ تلقائياً.")
                # محاولة بديلة: ربما اللاب بدأ بالفعل، ننتظر ظهور مهمة
                try:
                    await page.wait_for_selector("text=Task 1", timeout=15000)
                    send_tg("✅ اللاب قيد التشغيل بالفعل (ظهرت المهام)")
                except:
                    pass
            
            # صورة نهائية
            await page.screenshot(path="final.png", full_page=True)
            send_tg(f"🏁 المهمة انتهت. الرابط:\n{page.url}", "final.png")
            
        except Exception as e:
            send_tg(f"❌ خطأ غير متوقع: {str(e)[:200]}")
            await page.screenshot(path="error.png", full_page=True)
            send_tg("📸 لقطة الخطأ", "error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
