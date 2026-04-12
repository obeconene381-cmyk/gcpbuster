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
# معالجة الكابتشا - 10 طرق للنقر
# ============================================================
async def is_checkbox_checked(frame):
    """التحقق مما إذا تم تحديد الكابتشا"""
    try:
        result = await frame.evaluate("""
            () => {
                const checked = document.querySelector('.recaptcha-checkbox-checked');
                const input = document.querySelector('input[aria-checked="true"]');
                return (checked !== null) || (input !== null);
            }
        """)
        return result
    except:
        return False

async def click_captcha_checkbox(page):
    """10 طرق للنقر على checkbox الكابتشا"""

    # انتظار ظهور iframe الكابتشا (حتى 20 ثانية)
    send_tg("🤛 انتظار ظهور iframe الكابتشا...")
    anchor_frame = None
    for _ in range(20):
        for frame in page.frames:
            if "recaptcha/api2/anchor" in frame.url:
                anchor_frame = frame
                break
        if anchor_frame:
            break
        await asyncio.sleep(1)

    if not anchor_frame:
        send_tg("❌ لم يتم العثور على iframe الكابتشا")
        return False

    send_tg("✅ تم العثور على iframe الكابتشا")

    # انتظار تحميل المحتوى
    await asyncio.sleep(3)

    # ====== الطريقة 1: get_by_role ======
    try:
        send_tg("🎯 محاولة 1: get_by_role")
        checkbox = anchor_frame.get_by_role("checkbox").first
        if await checkbox.count() > 0:
            await checkbox.scroll_into_view_if_needed(timeout=5000)
            await checkbox.click(force=True, timeout=5000)
            await asyncio.sleep(3)
            if await is_checkbox_checked(anchor_frame):
                send_tg("✅ تم تحديد checkbox (طريقة 1)")
                return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 1 فشلت: {str(e)[:60]}")

    # ====== الطريقة 2: locator مباشر ======
    try:
        send_tg("🎯 محاولة 2: locator مباشر")
        checkbox = anchor_frame.locator(".recaptcha-checkbox-border").first
        if await checkbox.count() > 0:
            await checkbox.scroll_into_view_if_needed(timeout=5000)
            await checkbox.click(force=True, timeout=5000)
            await asyncio.sleep(3)
            if await is_checkbox_checked(anchor_frame):
                send_tg("✅ تم تحديد checkbox (طريقة 2)")
                return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 2 فشلت: {str(e)[:60]}")

    # ====== الطريقة 3: locator بالـ ID ======
    try:
        send_tg("🎯 محاولة 3: locator بالـ ID")
        checkbox = anchor_frame.locator("#recaptcha-anchor").first
        if await checkbox.count() > 0:
            await checkbox.scroll_into_view_if_needed(timeout=5000)
            await checkbox.click(force=True, timeout=5000)
            await asyncio.sleep(3)
            if await is_checkbox_checked(anchor_frame):
                send_tg("✅ تم تحديد checkbox (طريقة 3)")
                return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 3 فشلت: {str(e)[:60]}")

    # ====== الطريقة 4: النقر بالإحداثيات ======
    try:
        send_tg("🎯 محاولة 4: النقر بالإحداثيات")
        coords = await anchor_frame.evaluate("""
            () => {
                const el = document.querySelector('.recaptcha-checkbox-border') || 
                          document.querySelector('#recaptcha-anchor') ||
                          document.querySelector('[role="checkbox"]');
                if (el) {
                    const rect = el.getBoundingClientRect();
                    return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
                }
                return null;
            }
        """)
        if coords:
            await page.mouse.click(coords['x'], coords['y'])
            await asyncio.sleep(3)
            if await is_checkbox_checked(anchor_frame):
                send_tg("✅ تم تحديد checkbox (طريقة 4)")
                return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 4 فشلت: {str(e)[:60]}")

    # ====== الطريقة 5: JavaScript click ======
    try:
        send_tg("🎯 محاولة 5: JavaScript click")
        await anchor_frame.evaluate("""
            () => {
                const el = document.querySelector('.recaptcha-checkbox-border') || 
                          document.querySelector('#recaptcha-anchor') ||
                          document.querySelector('[role="checkbox"]');
                if (el) {
                    el.click();
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                    return true;
                }
                return false;
            }
        """)
        await asyncio.sleep(3)
        if await is_checkbox_checked(anchor_frame):
            send_tg("✅ تم تحديد checkbox (طريقة 5)")
            return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 5 فشلت: {str(e)[:60]}")

    # ====== الطريقة 6: dispatch_event ======
    try:
        send_tg("🎯 محاولة 6: dispatch_event")
        checkbox = anchor_frame.locator(".recaptcha-checkbox-border").first
        if await checkbox.count() > 0:
            await checkbox.dispatch_event("click")
            await asyncio.sleep(3)
            if await is_checkbox_checked(anchor_frame):
                send_tg("✅ تم تحديد checkbox (طريقة 6)")
                return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 6 فشلت: {str(e)[:60]}")

    # ====== الطريقة 7: focus + Enter ======
    try:
        send_tg("🎯 محاولة 7: focus + Enter")
        checkbox = anchor_frame.locator("#recaptcha-anchor").first
        if await checkbox.count() > 0:
            await checkbox.focus()
            await asyncio.sleep(1)
            await checkbox.press("Enter")
            await asyncio.sleep(3)
            if await is_checkbox_checked(anchor_frame):
                send_tg("✅ تم تحديد checkbox (طريقة 7)")
                return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 7 فشلت: {str(e)[:60]}")

    # ====== الطريقة 8: النقر على span الداخلي ======
    try:
        send_tg("🎯 محاولة 8: النقر على span الداخلي")
        checkbox = anchor_frame.locator("span.recaptcha-checkbox").first
        if await checkbox.count() > 0:
            await checkbox.scroll_into_view_if_needed(timeout=5000)
            await checkbox.click(force=True, timeout=5000)
            await asyncio.sleep(3)
            if await is_checkbox_checked(anchor_frame):
                send_tg("✅ تم تحديد checkbox (طريقة 8)")
                return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 8 فشلت: {str(e)[:60]}")

    # ====== الطريقة 9: tabindex ======
    try:
        send_tg("🎯 محاولة 9: البحث بـ tabindex")
        checkbox = anchor_frame.locator('[tabindex="0"]').first
        if await checkbox.count() > 0:
            await checkbox.scroll_into_view_if_needed(timeout=5000)
            await checkbox.click(force=True, timeout=5000)
            await asyncio.sleep(3)
            if await is_checkbox_checked(anchor_frame):
                send_tg("✅ تم تحديد checkbox (طريقة 9)")
                return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 9 فشلت: {str(e)[:60]}")

    # ====== الطريقة 10: querySelectorAll + index ======
    try:
        send_tg("🎯 محاولة 10: querySelectorAll")
        await anchor_frame.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    if (el.getAttribute('role') === 'checkbox' || 
                        el.classList.contains('recaptcha-checkbox-border')) {
                        el.click();
                        el.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                        return true;
                    }
                }
                return false;
            }
        """)
        await asyncio.sleep(3)
        if await is_checkbox_checked(anchor_frame):
            send_tg("✅ تم تحديد checkbox (طريقة 10)")
            return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 10 فشلت: {str(e)[:60]}")

    send_tg("❌ فشلت جميع محاولات النقر على checkbox")
    return False

async def handle_buster(page):
    """معالجة Buster"""
    send_tg("🔊 جاري البحث عن iframe التحدي...")

    # انتظار iframe التحدي
    challenge_frame = None
    for _ in range(20):
        for frame in page.frames:
            if "api2/bframe" in frame.url:
                challenge_frame = frame
                break
        if challenge_frame:
            break
        await asyncio.sleep(1)

    if not challenge_frame:
        send_tg("⚠️ لم يظهر iframe التحدي")
        return False

    send_tg("✅ تم العثور على iframe التحدي")
    await asyncio.sleep(3)

    # النقر على زر الصوت
    try:
        audio_btn = challenge_frame.locator("#recaptcha-audio-button").first
        if await audio_btn.count() > 0:
            await audio_btn.click(force=True, timeout=5000)
            send_tg("🔊 تم النقر على زر الصوت")
            await asyncio.sleep(3)
    except:
        pass

    # استخدام Buster
    for attempt in range(3):
        send_tg(f"🎯 Buster محاولة {attempt + 1}/3...")
        try:
            buster_btn = challenge_frame.locator("#solver-button").first
            if await buster_btn.count() > 0:
                await buster_btn.scroll_into_view_if_needed(timeout=3000)
                await buster_btn.click(force=True, timeout=5000)
            else:
                await challenge_frame.evaluate("document.querySelector('#solver-button').click()")

            await asyncio.sleep(20)
            send_tg(f"✅ Buster محاولة {attempt + 1} اكتملت")
        except Exception as e:
            send_tg(f"⚠️ Buster محاولة {attempt + 1}: {str(e)[:60]}")
        await asyncio.sleep(2)

    return True

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
