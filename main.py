import asyncio
import os
import zipfile
import requests
import re
from playwright.async_api import async_playwright

# --- الإعدادات الثابتة ---
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

# البروكسي الشغال 100%
WORKING_PROXY = {
    "server": "http://92.119.128.15:9996",
    "username": "user376353",
    "password": "y3ld6w"
}

# الكوكيز الخاصة بك
MY_COOKIES = [
    {"domain": ".skills.google", "name": "_ga", "value": "GA1.1.1438878037.1772447126", "path": "/"},
    {"domain": ".skills.google", "name": "_ga_2X30ZRBDSG", "value": "GS2.1.s1775996404$o97$g1$t1775996563$j32$l0$h0", "path": "/"},
    {"domain": "www.skills.google", "name": "_cvl-4_1_14_session", "value": "lQa%2FMnKdErx31nYRawt27XpphO7RO1Mod3%2FCk8T6PqZfkPZohBUhjBqhs2Mw1GIO229gr0KDHGkAp%2F9o7Blffpj%2BNy7YVlSwMKrQX3%2B0RxdyBzB0LU%2BFdcq5wLCPFWUPMhJNMngGjgVjse8JNXc1BO1j2FUpFQqvzAVGdPUShDJMshUZOva39naRS%2BVT%2BpBdaPE0I%2FgjsG6fC6KFeGqADXbUOQ36JiZQkoXYIjuKCxrOKwyaLKj7fFRebXiBduQKQIH3JK8bvcn0LkvK8BuvZ262zjAku4%2FkzRdFKfsfQMXrZStwGytxy1dqm%2FoQ6Lut8s9fnFVTGGcYIoJoxwba0Yx653S2FCemxd3GSCCqfGuNfuzRfNSCjsYvAeUmPdkQzepE80F3hbK15UUyM%2B2Puh3e4e%2FoovbnYf0xLZFGrxSpTcgJ5zb1FElGZ9LNFypWppJjbPlIySkS6X00pjko3fzmpi2TmUHvdBfPbn7ZmJbQ%2Fa8mQzvispzCN8GaAavsOZ%2FsD6xOt0%2FukYWX4oyXfRQg8AP8iZvYkj1iOvsbagPMKjp7utfL9DzDJ5n7LorhayjfSh9XLi1us38cm%2Fu8fzdbvLJn0DJ7koAN2V8V2KKLiGrU2H3e2z4pAFvTAmFENKac3LdIOOs2oNNj2Z8yF0iEnprV%2FzPeOb7eCcvFU66A6qb3f4SgUOTFVchEXizCrTx0%2FvdEQhoQG%2Boc3WXvnYtDbpPIuyt0BJSUda0e63hfWvQnww7DjHcdLtchLMoGYyOW0UktBRGkG3s%3D--TF35bd8CfnDqO%2BYr--Bp220SPOMrUj1y6NmvAiVw%3D%3D", "path": "/", "secure": True, "httpOnly": True},
    {"domain": "www.skills.google", "name": "user.id", "value": "eyJfcmFpbHMiOnsibWVzc2FnZSI6Ik1UTTNOVE13TmpJMyIsImV4cCI6bnVsbCwicHVyIjoiY29va2llLnVzZXIuaWQifX0%3D--3706d9f3abb091776145342b4e9be6e645941d44", "path": "/", "secure": True},
]

# --- دوال المساعدة ---
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
    dest = os.path.abspath("ext_folder")
    if os.path.exists("buster-main.zip"):
        with zipfile.ZipFile("buster-main.zip", 'r') as z:
            z.extractall(dest)
        for r, d, f in os.walk(dest):
            if "manifest.json" in f: return os.path.abspath(r)
    return dest

# --- تنفيذ المهمة ---
async def run():
    ext_path = await get_ext()
    user_data_dir = os.path.abspath("browser_profile") # بروفايل المتصفح
    
    async with async_playwright() as p:
        # 1. فتح المتصفح بوضع الـ Persistent لضمان عمل الإضافة
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            proxy=WORKING_PROXY,
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ],
            viewport={'width': 1280, 'height': 720}
        )
        
        # 2. حقن الكوكيز داخل الـ Context
        await context.add_cookies(MY_COOKIES)
        page = context.pages[0] if context.pages else await context.new_page()

        try:
            send_tg("🌐 فتح صفحة اللاب...")
            await page.goto(LAB_URL, timeout=90000, wait_until="commit")
            await page.wait_for_load_state("domcontentloaded", timeout=30000)

            # 3. الضغط على زر Start Lab
            pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)
            clicked_lab = False
            for _ in range(30):
                for target in [page] + list(page.frames):
                    btns = target.get_by_role("button", name=pattern)
                    if await btns.count() > 0:
                        await btns.first.click(force=True)
                        send_tg("✅ تم النقر على Start Lab")
                        clicked_lab = True
                        break
                if clicked_lab: break
                await asyncio.sleep(1)

            if clicked_lab:
                await asyncio.sleep(5)
                
                # 4. البحث عن مربع الكابتشا والنقر عليه
                found_check = False
                iframes = await page.locator('iframe').all()
                for iframe in iframes:
                    frame_content = iframe.content_frame
                    checkbox = frame_content.locator('.recaptcha-checkbox-border').first
                    if await checkbox.count() > 0:
                        await checkbox.click(force=True)
                        send_tg("✅ تم الضغط على مربع الكابتشا")
                        found_check = True
                        break
                
                if found_check:
                    await asyncio.sleep(5)
                    
                    # 5. الضغط على الشخص الأصفر (Buster)
                    send_tg("🕵️ جاري البحث عن الشخص الأصفر لحل التحدي...")
                    challenge_frame = page.frame_locator('iframe[src*="api2/bframe"]').first
                    buster_btn = challenge_frame.locator("#solver-button")
                    
                    try:
                        await buster_btn.wait_for(state="visible", timeout=12000)
                        await buster_btn.click(force=True)
                        send_tg("🎯 تم الضغط على الشخص الأصفر! ننتظر 6 ثوانٍ...")
                        
                        # انتظار 6 ثوانٍ كما طلبت
                        await asyncio.sleep(6)
                        
                        # 6. تصوير النتيجة (توقع ظهور Launch with 5 credits)
                        await page.screenshot(path="after_solve.png", full_page=True)
                        send_tg("📸 نتيجة التخطي ونافذة الـ Credits:", "after_solve.png")
                        
                        # محاولة الضغط على Launch with 5 Credits إذا ظهرت
                        launch_btn = page.get_by_role("button", name=re.compile(r"Launch\s*with\s*5\s*Credits", re.IGNORECASE))
                        if await launch_btn.count() > 0:
                            await launch_btn.first.click(force=True)
                            send_tg("🚀 تم الضغط على Launch with 5 Credits!")
                            await asyncio.sleep(5)
                            await page.screenshot(path="lab_started.png")
                            send_tg("📸 اللاب بدأ فعلياً:", "lab_started.png")
                            
                    except Exception as e:
                        send_tg("❌ الشخص الأصفر لم يظهر أو حدث خطأ في التخطي.")
                        await page.screenshot(path="error_buster.png")
                        send_tg("📸 لقطة شاشة للخطأ:", "error_buster.png")

        except Exception as e:
            send_tg(f"❌ خطأ عام في السكريبت: {str(e)[:150]}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run())
