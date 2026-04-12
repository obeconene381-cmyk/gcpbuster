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
# الدالة الناجحة من الكود الجديد (معدلة لزر Start Lab)
# ============================================================
async def click_start_lab_button(page, timeout_loop=120, post_click_wait=3):
    """
    نفس المنطق الناجح من الكود الجديد لكن مخصص لزر Start Lab
    """
    # نمط البحث عن "Start Lab" (غير حساس لحالة الأحرف)
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)

    async def _post_click_stabilize():
        """انتظار استقرار الصفحة بعد النقر"""
        try: 
            await page.wait_for_load_state("domcontentloaded", timeout=2000)
        except: 
            pass
        await asyncio.sleep(post_click_wait)

    # البحث في جميع الـ frames (الصفحة الرئيسية + iframes)
    for _ in range(timeout_loop):
        # نبحث في الصفحة الرئيسية وجميع الـ frames
        targets = [page] + list(page.frames)

        for target in targets:
            try:
                # الطريقة 1: البحث باستخدام get_by_role (الأفضل)
                btns = target.get_by_role("button", name=pattern)
                count = await btns.count()

                # نبحث من الأخير إلى الأول (في حالة وجود أزرار متعددة)
                for i in range(count - 1, -1, -1):
                    b = btns.nth(i)

                    # التحقق من أن الزر مرئي ومفعّل
                    if await b.is_visible() and await b.is_enabled():
                        # التمرير إلى الزر
                        await b.scroll_into_view_if_needed(timeout=1000)

                        # النقر مع force=True دائماً (لتجاوز أي overlay)
                        await b.click(timeout=3000, force=True)

                        # انتظار الاستقرار
                        await _post_click_stabilize()

                        send_tg("✅ تم النقر على Start Lab (get_by_role)")
                        return True

            except Exception as e:
                continue

        # انتظار ثانية قبل المحاولة التالية
        await asyncio.sleep(1)

    # إذا فشلت الطريقة 1، نجرب الطريقة 2: البحث باستخدام locator العام
    for _ in range(60):  # 60 ثانية إضافية
        for target in [page] + list(page.frames):
            try:
                # البحث باستخدام locator عام
                locators = [
                    target.locator('button:has-text("Start Lab")'),
                    target.locator('button.ql-button--primary'),
                    target.locator('button.start-lab-button'),
                    target.locator('[data-testid="start-lab-button"]'),
                ]

                for loc in locators:
                    count = await loc.count()
                    for i in range(count):
                        b = loc.nth(i)
                        if await b.is_visible() and await b.is_enabled():
                            await b.scroll_into_view_if_needed(timeout=1000)
                            await b.click(timeout=3000, force=True)
                            await _post_click_stabilize()
                            send_tg("✅ تم النقر على Start Lab (locator)")
                            return True
            except:
                continue
        await asyncio.sleep(1)

    return False

# ============================================================
# معالجة الكابتشا (نفس المنطق الناجح)
# ============================================================
async def handle_recaptcha(page):
    """معالجة reCAPTCHA باستخدام Buster"""
    try:
        await asyncio.sleep(2)

        for frame in page.frames:
            if "recaptcha/api2/anchor" in frame.url:
                send_tg("🤖 كابتشا detected")

                # النقر على checkbox
                try:
                    checkbox = frame.get_by_role("checkbox").first
                    if await checkbox.count() > 0:
                        await checkbox.click(timeout=3000, force=True)
                        await asyncio.sleep(5)
                except:
                    pass

                # البحث عن iframe التحدي
                for f in page.frames:
                    if "api2/bframe" in f.url:
                        send_tg("🔊 استخدام Buster...")
                        try:
                            # النقر على زر الصوت
                            audio_btn = f.locator("#recaptcha-audio-button").first
                            if await audio_btn.count() > 0:
                                await audio_btn.click(timeout=3000, force=True)
                                await asyncio.sleep(2)

                            # استخدام Buster
                            buster_btn = f.locator("#solver-button").first
                            if await buster_btn.count() > 0:
                                await buster_btn.click(timeout=3000, force=True)
                                await asyncio.sleep(15)
                        except:
                            pass
                return True
    except:
        pass
    return False

async def run():
    send_tg("🚀 بدء المهمة (باستخدام المنطق الناجح)...")
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

            # زيادة المهلة إلى 10 دقائق
            await page.goto(LAB_URL, timeout=600000, wait_until="domcontentloaded")
            await asyncio.sleep(5)

            await page.screenshot(path="lab_page.png", full_page=True)
            send_tg("📸 صفحة اللاب مفتوحة", "lab_page.png")

            # محاولة النقر على Start Lab باستخدام المنطق الناجح
            clicked = await click_start_lab_button(page, timeout_loop=120, post_click_wait=5)

            if clicked:
                send_tg("✅ تم النقر بنجاح، انتظار...")
                await asyncio.sleep(10)

                # معالجة الكابتشا
                await handle_recaptcha(page)

                # انتظار أطول لتحميل اللاب
                await asyncio.sleep(15)

                await page.screenshot(path="after_start.png", full_page=True)
                send_tg("📸 بعد الضغط", "after_start.png")
            else:
                send_tg("❌ فشل في النقر على Start Lab بعد جميع المحاولات")

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
