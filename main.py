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

# ============================================================
# معالجة الكابتشا - إصلاح قوي مع التحقق الفعلي
# ============================================================
async def handle_recaptcha_robust(page):
    """معالجة الكابتشا مع التحقق الفعلي من النجاح"""
    send_tg("🤖 جاري معالجة الكابتشا...")

    # انتظار ظهور الكابتشا
    await asyncio.sleep(3)

    # البحث عن iframe الكابتشا
    anchor_frame = None
    for _ in range(10):  # محاولة 10 مرات
        for frame in page.frames:
            if "recaptcha/api2/anchor" in frame.url:
                anchor_frame = frame
                break
        if anchor_frame:
            break
        await asyncio.sleep(1)

    if not anchor_frame:
        send_tg("⚠️ لم يتم العثور على iframe الكابتشا")
        return False

    send_tg("✅ تم العثور على iframe الكابتشا")

    # ====== النقر على Checkbox باستخدام Playwright (ليس JavaScript فقط) ======
    checkbox_clicked = False

    # محاولة 1: استخدام get_by_role
    try:
        checkbox = anchor_frame.get_by_role("checkbox").first
        if await checkbox.count() > 0:
            await checkbox.scroll_into_view_if_needed(timeout=3000)
            await checkbox.click(timeout=5000, force=True)
            await asyncio.sleep(2)

            # التحقق الفعلي
            is_checked = await anchor_frame.evaluate("() => document.querySelector('.recaptcha-checkbox-checked') !== null")
            if is_checked:
                checkbox_clicked = True
                send_tg("✅ Checkbox تم تحديده (get_by_role)")
    except Exception as e:
        send_tg(f"⚠️ محاولة 1: {str(e)[:80]}")

    # محاولة 2: استخدام locator مباشر على العنصر
    if not checkbox_clicked:
        try:
            checkbox_loc = anchor_frame.locator(".recaptcha-checkbox-border").first
            if await checkbox_loc.count() > 0:
                await checkbox_loc.scroll_into_view_if_needed(timeout=3000)
                await checkbox_loc.click(timeout=5000, force=True)
                await asyncio.sleep(2)

                is_checked = await anchor_frame.evaluate("() => document.querySelector('.recaptcha-checkbox-checked') !== null")
                if is_checked:
                    checkbox_clicked = True
                    send_tg("✅ Checkbox تم تحديده (locator)")
        except Exception as e:
            send_tg(f"⚠️ محاولة 2: {str(e)[:80]}")

    # محاولة 3: استخدام الإحداثيات
    if not checkbox_clicked:
        try:
            box = await anchor_frame.evaluate("""
                () => {
                    const el = document.querySelector('.recaptcha-checkbox-border') || 
                              document.querySelector('#recaptcha-anchor');
                    if (el) {
                        const rect = el.getBoundingClientRect();
                        return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
                    }
                    return null;
                }
            """)
            if box:
                await page.mouse.click(box['x'], box['y'])
                await asyncio.sleep(2)

                is_checked = await anchor_frame.evaluate("() => document.querySelector('.recaptcha-checkbox-checked') !== null")
                if is_checked:
                    checkbox_clicked = True
                    send_tg("✅ Checkbox تم تحديده (coordinates)")
        except Exception as e:
            send_tg(f"⚠️ محاولة 3: {str(e)[:80]}")

    if not checkbox_clicked:
        send_tg("❌ فشل تحديد checkbox")
        return False

    # ====== انتظار ظهور التحدي ======
    send_tg("⏳ انتظار ظهور التحدي...")
    await asyncio.sleep(5)

    # البحث عن iframe التحدي
    challenge_frame = None
    for _ in range(15):
        for frame in page.frames:
            if "api2/bframe" in frame.url:
                challenge_frame = frame
                break
        if challenge_frame:
            break
        await asyncio.sleep(1)

    if not challenge_frame:
        send_tg("⚠️ لم يظهر التحدي (ربما تم حلها تلقائياً)")
        return True  # ربما تم حلها

    send_tg("🔊 تم العثور على iframe التحدي")

    # ====== النقر على زر الصوت ======
    audio_clicked = False
    try:
        # انتظار زر الصوت
        for _ in range(5):
            try:
                audio_btn = challenge_frame.locator("#recaptcha-audio-button").first
                if await audio_btn.count() > 0:
                    await audio_btn.click(timeout=3000, force=True)
                    audio_clicked = True
                    send_tg("✅ تم النقر على زر الصوت")
                    await asyncio.sleep(3)
                    break
            except:
                await asyncio.sleep(1)
    except:
        pass

    if not audio_clicked:
        try:
            await challenge_frame.evaluate("document.querySelector('#recaptcha-audio-button').click()")
            send_tg("✅ زر الصوت (JavaScript)")
            await asyncio.sleep(3)
        except:
            pass

    # ====== استخدام Buster ======
    for attempt in range(3):
        send_tg(f"🎯 Buster محاولة {attempt + 1}/3...")

        try:
            # البحث عن زر Buster
            buster_btn = challenge_frame.locator("#solver-button").first

            if await buster_btn.count() > 0:
                await buster_btn.scroll_into_view_if_needed(timeout=2000)
                await buster_btn.click(timeout=5000, force=True)
            else:
                # محاولة JavaScript
                await challenge_frame.evaluate("document.querySelector('#solver-button').click()")

            # انتظار أطول (20 ثانية)
            await asyncio.sleep(20)

            # التحقق من الحل
            is_solved = await anchor_frame.evaluate("""
                () => {
                    const checked = document.querySelector('.recaptcha-checkbox-checked');
                    const error = document.querySelector('.recaptcha-error-message');
                    return checked !== null && error === null;
                }
            """)

            if is_solved:
                send_tg("✅ Buster نجح!")
                return True
            else:
                send_tg(f"⚠️ Buster محاولة {attempt + 1} لم تحلها")

        except Exception as e:
            send_tg(f"⚠️ Buster خطأ: {str(e)[:80]}")

        await asyncio.sleep(3)

    send_tg("❌ فشل حل الكابتشا")
    return False

async def run():
    send_tg("🚀 بدء المهمة (إصلاح الكابتشا)...")
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

            # ====== النقر على Start Lab ======
            clicked = await click_start_lab_button(page, timeout_loop=120, post_click_wait=3)

            if clicked:
                # ⏱️ انتظار 5 ثوانٍ فقط (كان 10)
                send_tg("⏳ انتظار 5 ثوانٍ...")
                await asyncio.sleep(5)

                # ====== معالجة الكابتشا (إصلاح قوي) ======
                await handle_recaptcha_robust(page)

                # انتظار إضافي
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
