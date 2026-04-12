import asyncio
import os
import zipfile
import requests
import re
from playwright.async_api import async_playwright

BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"
BUSTER_EXTENSION_URL = "https://chrome.google.com/webstore/detail/buster-captcha-solver-for/mpbjkejclgfgadiemmefgebjfooflfhl?hl=en"

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

async def human_click(page, locator):
    """محاكاة النقر البشري"""
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

# --- دالة تثبيت Buster من المتجر (مثل الفيديو) ---
async def install_buster_from_store(page):
    send_tg("🔧 جاري تثبيت Buster من Chrome Web Store...")
    
    try:
        # الذهاب لصفحة الإضافة
        await page.goto(BUSTER_EXTENSION_URL, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle", timeout=30000)
        await asyncio.sleep(3)
        
        send_tg("📸 صفحة الإضافة محملة، جاري الضغط على Add to Chrome...")
        
        # الضغط على زر Add to Chrome (محاولة متعددة)
        clicked = False
        
        # المحاولة 1: بالنص
        try:
            btn = page.get_by_role("button", name=re.compile(r"Add to Chrome", re.I))
            if await btn.count() > 0:
                await btn.first.click(force=True)
                clicked = True
                send_tg("✅ تم الضغط على 'Add to Chrome' (طريقة 1)")
        except: pass
        
        # المحاولة 2: بالـ CSS
        if not clicked:
            try:
                btn = page.locator('button:has-text("Add to Chrome")')
                if await btn.count() > 0:
                    await btn.first.click(force=True)
                    clicked = True
                    send_tg("✅ تم الضغط على 'Add to Chrome' (طريقة 2)")
            except: pass
        
        # المحاولة 3: JS
        if not clicked:
            try:
                await page.evaluate('() => { const btn = document.querySelector("button"); if(btn) btn.click(); }')
                clicked = True
                send_tg("✅ تم الضغط على 'Add to Chrome' (طريقة 3 - JS)")
            except: pass
        
        if not clicked:
            send_tg("❌ فشل الضغط على Add to Chrome")
            return False
        
        await asyncio.sleep(3)
        
        # الضغط على Add extension في الـ Dialog
        send_tg("⏳ انتظار نافذة التأكيد...")
        ext_clicked = False
        
        try:
            # البحث عن الزر في الـ dialog (قد يكون في نفس الصفحة)
            ext_btn = page.get_by_role("button", name=re.compile(r"Add extension", re.I))
            if await ext_btn.count() > 0:
                await ext_btn.first.click(force=True)
                ext_clicked = True
                send_tg("✅ تم الضغط على 'Add extension'")
        except: pass
        
        if not ext_clicked:
            try:
                ext_btn = page.locator('button:has-text("Add extension")')
                if await ext_btn.count() > 0:
                    await ext_btn.first.click(force=True)
                    ext_clicked = True
                    send_tg("✅ تم الضغط على 'Add extension' (طريقة 2)")
            except: pass
        
        if not ext_clicked:
            try:
                # محاولة الضغط عبر JS على الزر الثاني عادةً
                await page.evaluate('() => { const btns = document.querySelectorAll("button"); if(btns.length > 1) btns[1].click(); }')
                ext_clicked = True
                send_tg("✅ تم الضغط على 'Add extension' (طريقة 3 - JS)")
            except: pass
        
        if not ext_clicked:
            send_tg("❌ فشل الضغط على Add extension")
            return False
        
        # انتظار التثبيت (10 ثوانٍ كما في الفيديو)
        send_tg("⏳ انتظار اكتمال التثبيت...")
        await asyncio.sleep(10)
        
        # التقاط صورة التأكيد (يجب أن تظهر رسالة "has been added to Chrome")
        await page.screenshot(path="buster_installed.png", full_page=True)
        send_tg("📸 ✅ تم تثبيت Buster بنجاح:", "buster_installed.png")
        
        return True
        
    except Exception as e:
        send_tg(f"❌ خطأ في تثبيت Buster: {str(e)[:200]}")
        try:
            await page.screenshot(path="install_error.png")
            send_tg("📸 خطأ:", "install_error.png")
        except: pass
        return False

# --- دالة Start Lab ---
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

# --- دالة الكابتشا مع النقر البشري ---
async def click_captcha_checkbox(page):
    send_tg("🤛 جاري البحث عن مربع الكابتشا...")
    try:
        await asyncio.sleep(3)
        iframes = await page.locator('iframe').all()
        
        for iframe in iframes:
            try:
                frame_content = iframe.content_frame
                checkbox = frame_content.locator('.recaptcha-checkbox-border').first
                
                if await checkbox.count() > 0 and await checkbox.is_visible():
                    # استخدام النقر البشري
                    success = await human_click(page, checkbox)
                    if success:
                        send_tg("✅ تم الضغط على المربع بنجاح (نقر بشري)")
                        await asyncio.sleep(2)
                        return True
            except: continue
        
        send_tg("❌ لم يتم العثور على مربع الكابتشا")
        return False
    except: return False

# --- دالة Buster ---
async def handle_buster(page):
    send_tg("🕵️ جاري البحث عن الشخص الأصفر...")
    try:
        # انتظار ظهور iframe التحدي
        challenge_frame = page.frame_locator('iframe[title*="challenge"], iframe[src*="api2/bframe"]').first
        buster_btn = challenge_frame.locator("#solver-button")
        
        await buster_btn.wait_for(state="visible", timeout=15000)
        await buster_btn.click(force=True)
        send_tg("🎯 تم الضغط على الشخص الأصفر!")
        
        # انتظار الحل (6 ثوانٍ كما طلبت)
        await asyncio.sleep(6)
        return True
    except Exception as e:
        send_tg(f"❌ الشخص الأصفر لم يظهر: {str(e)[:100]}")
        return False

# --- دالة Launch Credits ---
async def click_launch_credits(page):
    try:
        pattern = re.compile(r"Launch\s*with\s*(\d+\s*)?Credits?", re.IGNORECASE)
        btn = page.get_by_role("button", name=pattern)
        
        if await btn.count() > 0:
            await btn.first.click(force=True)
            send_tg("🚀 تم الضغط على Launch with Credits!")
            await asyncio.sleep(3)
            return True
    except: pass
    return False

# --- التشغيل الرئيسي ---
async def run():
    send_tg("🚀 بدء المهمة الكاملة...")
    
    async with async_playwright() as p:
        # إنشاء مجلد للبروفايل
        user_data_dir = "/tmp/chrome_profile"
        os.makedirs(user_data_dir, exist_ok=True)
        
        # فتح متصفح مع بروفايل مستمر (مهم جداً للإضافات)
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            proxy=WORKING_PROXY,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ],
            viewport={'width': 1280, 'height': 720}
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        try:
            # الخطوة 1: تثبيت Buster من المتجر (مثل الفيديو)
            buster_installed = await install_buster_from_store(page)
            
            if not buster_installed:
                send_tg("⚠️ تحذير: لم يتم تثبيت Buster، لكن سأحاول المتابعة...")
            
            # الخطوة 2: فتح صفحة اللاب
            send_tg("🌐 فتح صفحة اللاب...")
            await context.add_cookies(MY_COOKIES)
            
            # فتح اللاب في نفس الصفحة أو صفحة جديدة
            await page.goto(LAB_URL, timeout=90000, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            await page.screenshot(path="lab_loaded.png", full_page=True)
            send_tg("📸 تم تحميل اللاب:", "lab_loaded.png")

            # الخطوة 3: الضغط على Start Lab
            if await click_start_lab_button(page):
                await asyncio.sleep(5)
                
                # الخطوة 4: الضغط على الكابتشا
                if await click_captcha_checkbox(page):
                    await asyncio.sleep(4)
                    
                    # الخطوة 5: الضغط على Buster (الشخص الأصفر)
                    await handle_buster(page)
                    
                    # الخطوة 6: الضغط على Launch Credits إن وجد
                    await click_launch_credits(page)
                    
                    # النتيجة النهائية
                    await asyncio.sleep(2)
                    await page.screenshot(path="final_result.png", full_page=True)
                    send_tg("📸 ✅ النتيجة النهائية:", "final_result.png")
                else:
                    await page.screenshot(path="captcha_failed.png", full_page=True)
                    send_tg("❌ فشل الضغط على الكابتشا:", "captcha_failed.png")
            else:
                send_tg("❌ لم أجد زر Start Lab")

        except Exception as e:
            send_tg(f"❌ خطأ عام: {str(e)[:200]}")
            try:
                await page.screenshot(path="error_general.png", full_page=True)
                send_tg("📸 خطأ:", "error_general.png")
            except: pass
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run())
