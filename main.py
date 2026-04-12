import asyncio
import os
import zipfile
import requests
import re
from playwright.async_api import async_playwright

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

# --- دالة الضغط على Start Lab (كما هي بدون تغيير) ---
async def click_start_lab_button(page):
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)
    for _ in range(60): 
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

# --- دالة الضغط على الكابتشا (تم إصلاحها لتكون أقوى) ---
async def click_captcha_checkbox(page):
    send_tg("🤛 جاري محاولة صيد مربع الكابتشا...")
    try:
        # الانتظار قليلاً حتى يستقر الفريم
        await asyncio.sleep(5)
        
        # استهداف فريم الـ anchor مباشرة (أضمن طريقة في Playwright)
        anchor_frame = page.frame_locator('iframe[src*="api2/anchor"]').first
        checkbox = anchor_frame.locator('#recaptcha-anchor').first
        
        # الانتظار حتى يصبح المربع مرئياً
        await checkbox.wait_for(state="visible", timeout=15000)
        
        if await checkbox.count() > 0:
            # الضغط مع تأخير بسيط لمحاكاة البشر
            await checkbox.click(force=True, delay=200)
            send_tg("✅ تم الضغط على المربع بنجاح")
            return True
            
        # خطة بديلة لو فشل الاستهداف المباشر
        iframes = await page.locator('iframe').all()
        for iframe in iframes:
            frame_content = iframe.content_frame
            if frame_content:
                check = frame_content.locator('.recaptcha-checkbox-border').first
                if await check.count() > 0:
                    await check.click(force=True, delay=200)
                    send_tg("✅ تم الضغط على المربع (طريقة 2)")
                    return True
                    
        send_tg("❌ لم أستطع العثور على المربع.")
        return False
    except Exception as e:
        send_tg(f"❌ خطأ في دالة المربع: {str(e)[:50]}")
        return False

# --- دالة التخطي بالشخص الأصفر ---
async def handle_buster_direct(page):
    send_tg("🕵️ جاري البحث عن الشخص الأصفر داخل الفريم...")
    try:
        challenge_frame = page.frame_locator('iframe[title*="challenge"], iframe[src*="api2/bframe"]').first
        buster_btn = challenge_frame.locator("#solver-button")
        
        # انتظار طويل قليلاً للتأكد من حقن الإضافة
        await buster_btn.wait_for(state="visible", timeout=15000)
        
        await buster_btn.click(force=True)
        send_tg("🎯 تم الضغط على الشخص الأصفر! ننتظر 8 ثوانٍ...")
        await asyncio.sleep(8)
        
    except Exception as e:
        send_tg("❌ الشخص الأصفر لم يظهر.")

# --- التشغيل الرئيسي ---
async def run():
    send_tg("🚀 بدء المهمة...")
    ext_path = await get_ext()
    
    async with async_playwright() as p:
        # ملاحظة: إذا كنت على Pydroid، يفضل دائماً استخدام headless=True
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
        
        context = await browser.new_context(proxy=WORKING_PROXY)
        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()

        try:
            send_tg("🌐 فتح صفحة اللاب...")
            await page.goto(LAB_URL, timeout=90000, wait_until="commit")
            await page.wait_for_load_state("domcontentloaded", timeout=30000)
            
            if await click_start_lab_button(page):
                await asyncio.sleep(5)
                
                # الضغط على المربع (الدالة المصلحة)
                if await click_captcha_checkbox(page):
                    await asyncio.sleep(5)
                    
                    # تخطي الكابتشا
                    await handle_buster_direct(page)
                    
                    # تصوير النتيجة
                    await page.screenshot(path="final_result.png", full_page=True)
                    send_tg("📸 النتيجة النهائية:", "final_result.png")
                    
                    # فحص زر الـ Credits
                    try:
                        launch_btn = page.locator("text=Launch with 5 Credits").first
                        if await launch_btn.count() > 0:
                            send_tg("✅ نافذة Credits ظهرت!")
                    except: pass
                else:
                    send_tg("❌ فشل في تجاوز خطوة المربع")
            else:
                send_tg("❌ لم أجد زر Start Lab")

        except Exception as e:
            send_tg(f"❌ خطأ عام: {str(e)[:100]}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
