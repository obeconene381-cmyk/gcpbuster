import asyncio
import os
import zipfile
import requests
import re
from playwright.async_api import async_playwright

BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

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

# ============================================================
# نفس دالة النقر على Start Lab (لا تغيير)
# ============================================================
async def click_start_lab_button(page, timeout_loop=120, post_click_wait=3):
    """نفس المنطق الناجح - لا تغيير"""
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)

    async def _post_click_stabilize():
        try: 
            await page.wait_for_load_state("domcontentloaded", timeout=2000)
        except: 
            pass
        await asyncio.sleep(post_click_wait)

    for _ in range(timeout_loop):
        targets = [page] + list(page.frames)

        for target in targets:
            try:
                btns = target.get_by_role("button", name=pattern)
                for i in range(await btns.count() - 1, -1, -1):
                    b = btns.nth(i)
                    if await b.is_visible() and await b.is_enabled():
                        await b.scroll_into_view_if_needed(timeout=1000)
                        await b.click(timeout=3000, force=True)
                        await _post_click_stabilize()
                        send_tg("✅ تم النقر على Start Lab")
                        return True
            except:
                continue
        await asyncio.sleep(1)

    return False

async def click_captcha_checkbox(page):
    """طريقة واحدة نظيفة وقوية باستخدام frame_locator للتعامل مع الـ iframe الديناميكي"""
    send_tg("🤛 محاولة النقر على مربع الكابتشا...")
    try:
        # استخدام frame_locator هو الأفضل للـ iframes في Playwright
        captcha_frame = page.frame_locator('iframe[src*="api2/anchor"]').first
        
        # تحديد مربع الاختيار
        checkbox = captcha_frame.locator('#recaptcha-anchor')
        
        # الانتظار حتى يصبح المربع مرئياً وموجوداً في الـ DOM
        await checkbox.wait_for(state="visible", timeout=20000)
        
        # التمرير إليه لضمان ظهوره في الشاشة
        await checkbox.scroll_into_view_if_needed()
        
        # محاكاة حركة الماوس وتأخير النقر لتبدو كحركة بشرية
        await checkbox.hover()
        await asyncio.sleep(0.5)
        await checkbox.click(delay=150)
        
        send_tg("✅ تم النقر على مربع الكابتشا")
        return True
    except Exception as e:
        send_tg(f"❌ فشل النقر على مربع الكابتشا: {str(e)[:60]}")
        return False

async def handle_buster(page):
    """معالجة Buster وتجنب خطأ TypeError الذي ظهر لك"""
    send_tg("🔊 جاري البحث عن نافذة التحدي (Buster)...")
    try:
        # الوصول لـ iframe التحدي
        challenge_frame = page.frame_locator('iframe[src*="api2/bframe"]').first
        
        # تحديد زر الصوت
        audio_btn = challenge_frame.locator("#recaptcha-audio-button")
        
        # الانتظار حتى يظهر زر الصوت (في حال ظهر التحدي أصلاً)
        await audio_btn.wait_for(state="visible", timeout=10000)
        await audio_btn.click(delay=150)
        send_tg("🔊 تم النقر على زر الصوت")
        await asyncio.sleep(2)
        
        # تحديد زر Buster
        buster_btn = challenge_frame.locator("#solver-button")
        await buster_btn.wait_for(state="visible", timeout=5000)
        
        for attempt in range(3):
            send_tg(f"🎯 Buster محاولة {attempt + 1}/3...")
            try:
                await buster_btn.click(delay=100)
                await asyncio.sleep(15) # انتظار Buster ليقوم بجلب وحل الصوت
                send_tg(f"✅ Buster محاولة {attempt + 1} اكتملت")
                break # الخروج من الحلقة عند النجاح
            except Exception as e:
                send_tg(f"⚠️ Buster محاولة {attempt + 1} فشلت: {str(e)[:60]}")
                await asyncio.sleep(2)
        return True
    except Exception as e:
        send_tg("⚠️ لم يظهر تحدي الصوت أو تم التجاوز التلقائي.")
        return False


async def run():
    send_tg("🚀 بدء المهمة (كود قوي للكابتشا)...")
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
                "--window-size=1280,720",
                "--lang=en-US"
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            locale="en-US"
        )

        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()

        try:
            send_tg("🌐 فتح صفحة اللاب...")
            await page.goto(LAB_URL, timeout=600000, wait_until="domcontentloaded")
            await asyncio.sleep(5)

            await page.screenshot(path="lab_page.png", full_page=True)
            send_tg("📸 صفحة اللاب مفتوحة", "lab_page.png")

            # النقر على Start Lab
            clicked = await click_start_lab_button(page, timeout_loop=120, post_click_wait=3)

            if clicked:
                send_tg("⏳ انتظار 5 ثوانٍ...")
                await asyncio.sleep(5)

                # معالجة الكابتشا (10 طرق)
                await click_captcha_checkbox(page)

                # معالجة Buster
                await handle_buster(page)

                await asyncio.sleep(10)
                await page.screenshot(path="after_start.png", full_page=True)
                send_tg("📸 بعد الضغط", "after_start.png")
            else:
                send_tg("❌ فشل في النقر على Start Lab")

            await page.screenshot(path="final.png", full_page=True)
            send_tg(f"🏁 انتهت المهمة\n🔗 {page.url}", "final.png")

        except Exception as e:
            send_tg(f"❌ خطأ: {str(e)[:200]}")
            try:
                await page.screenshot(path="error.png", full_page=True)
                send_tg("📸 لقطة الخطأ", "error.png")
            except:
                pass
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
