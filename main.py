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

# النسخة الجاهزة للكروم (Compiled Release)
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
    ext_dir = os.path.abspath("buster_compiled_ext")
    if os.path.exists(ext_dir): shutil.rmtree(ext_dir)
    os.makedirs(ext_dir)
    zip_path = "buster_ready.zip"
    try:
        send_tg("📥 جاري تحميل النسخة الرسمية الجاهزة للإضافة...")
        r = requests.get(BUSTER_COMPILED_URL, timeout=30)
        with open(zip_path, "wb") as f: f.write(r.content)
        with zipfile.ZipFile(zip_path, 'r') as z: z.extractall(ext_dir)
        os.remove(zip_path)
        send_tg(f"✅ تم تجهيز الإضافة الجاهزة في المسار: {ext_dir}")
        return ext_dir
    except Exception as e:
        send_tg(f"❌ فشل تحميل الإضافة: {e}")
        return None

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

async def dismiss_credits_modal(page):
    try:
        btn = page.get_by_role("button", name=re.compile(r"Dismiss", re.I))
        if await btn.count() > 0 and await btn.first.is_visible():
            await btn.first.click()
            send_tg("✅ تم إغلاق نافذة Credits Expiring.")
            await asyncio.sleep(2)
            return True
    except: pass
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

# --- تعديل منطق البحث عن الشخص الأصفر (Buster) ليكون أكثر دقة ---
async def handle_buster(page):
    send_tg("🕵️ البحث عن الشخص الأصفر...")
    try:
        # الانتظار الكافي لظهور إطار التحدي (Challenge Iframe)
        await asyncio.sleep(5)
        
        target_btn = None
        # البحث في جميع الإطارات (Frames) المفتوحة في الصفحة عن زر Buster
        for frame in page.frames:
            try:
                # محاولة تحديد زر Buster داخل كل إطار
                btn = frame.locator("#solver-button")
                if await btn.count() > 0:
                    target_btn = btn
                    break
            except:
                continue
        
        if target_btn:
            # الانتظار ليكون الزر قابلاً للتفاعل
            await target_btn.wait_for(state="visible", timeout=10000)
            
            # استخدام دالة النقر البشري الخاصة بك
            success = await human_click(page, target_btn)
            if success:
                send_tg("🎯 تم الضغط على الشخص الأصفر بنجاح!")
            else:
                await target_btn.click(force=True)
                send_tg("🎯 تم الضغط على الشخص الأصفر (نقر إجباري)!")
                
            await asyncio.sleep(8) # انتظار حل الكابتشا
            return True
        else:
            send_tg("❌ لم يتم العثور على زر Buster في أي إطار (Frame)")
            await page.screenshot(path="buster_not_found.png")
            send_tg("📸 صورة للتحقق من الحالة:", "buster_not_found.png")
            return False
    except Exception as e:
        send_tg(f"❌ خطأ في التعامل مع Buster: {str(e)[:100]}")
        return False
# -----------------------------------------------------------------

async def run():
    send_tg("🚀 بدء المهمة...")
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
            await page.goto(LAB_URL, timeout=60000)
            await asyncio.sleep(4)
            await dismiss_credits_modal(page)
            
            if await click_start_lab_button(page):
                await asyncio.sleep(5)
                if await click_captcha_checkbox(page):
                    await handle_buster(page)
                    await asyncio.sleep(5)
                    await page.screenshot(path="final_result.png")
                    send_tg("📸 النتيجة النهائية للمهمة:", "final_result.png")
                else:
                    send_tg("❌ لم يظهر مربع الكابتشا")
        except Exception as e:
            send_tg(f"🔥 خطأ غير متوقع: {e}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run())
