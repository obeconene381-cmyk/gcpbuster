import asyncio
import os
import zipfile
import requests
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

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

async def advanced_click_start_lab(page):
    """طرق متقدمة للنقر على الزر"""

    send_tg("🔍 البحث المتقدم عن زر Start Lab...")

    # الانتظار الطويل لضمان تحميل الصفحة
    await asyncio.sleep(5)

    # ====== الطريقة 1: البحث في Shadow DOM ======
    try:
        result = await page.evaluate("""
            () => {
                function findInShadowDOM(root, selector) {
                    const elements = [];
                    const elems = root.querySelectorAll(selector);
                    elements.push(...elems);

                    const all = root.querySelectorAll('*');
                    for (const el of all) {
                        if (el.shadowRoot) {
                            elements.push(...findInShadowDOM(el.shadowRoot, selector));
                        }
                    }
                    return elements;
                }

                const buttons = findInShadowDOM(document, 'button');
                const target = buttons.find(btn => {
                    const text = (btn.innerText || btn.textContent || '').trim();
                    return text.toLowerCase().includes('start lab') && !text.toLowerCase().includes('starter');
                });

                if (target) {
                    target.scrollIntoView({block: 'center'});
                    target.click();
                    return {success: true, method: 'shadow DOM'};
                }
                return {success: false};
            }
        """)

        if result and result.get('success'):
            send_tg("✅ تم النقر (Shadow DOM)")
            await asyncio.sleep(3)
            return True
    except:
        pass

    # ====== الطريقة 2: Dispatch events كاملة (mousedown, mouseup, click) ======
    try:
        btn = page.locator('button:has-text("Start Lab")').first
        await btn.wait_for(state="visible", timeout=10000)

        box = await btn.bounding_box()
        if box:
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2

            # نقل الماوس إلى الزر أولاً (hover)
            await page.mouse.move(x, y)
            await asyncio.sleep(0.5)

            # mousedown
            await page.mouse.down()
            await asyncio.sleep(0.1)

            # mouseup
            await page.mouse.up()
            await asyncio.sleep(0.5)

            send_tg("✅ تم النقر (Mouse events complete)")
            return True
    except Exception as e:
        send_tg(f"⚠️ Mouse events failed: {str(e)[:100]}")

    # ====== الطريقة 3: استخدام page.press (Enter) ======
    try:
        btn = page.locator('button:has-text("Start Lab")').first
        await btn.focus()
        await asyncio.sleep(0.5)
        await page.press('button:has-text("Start Lab")', 'Enter')
        send_tg("✅ تم النقر (Enter key)")
        return True
    except:
        pass

    # ====== الطريقة 4: الضغط على الإحداثيات بدقة عالية ======
    try:
        # الحصول على إحداثيات الزر من JavaScript
        coords = await page.evaluate("""
            () => {
                const btn = [...document.querySelectorAll('button')].find(b => 
                    b.innerText.toLowerCase().includes('start lab') && 
                    !b.innerText.toLowerCase().includes('starter')
                );
                if (btn) {
                    const rect = btn.getBoundingClientRect();
                    return {
                        x: rect.left + rect.width / 2,
                        y: rect.top + rect.height / 2
                    };
                }
                return null;
            }
        """)

        if coords:
            await page.mouse.click(coords['x'], coords['y'])
            send_tg(f"✅ تم النقر (Coordinates: {int(coords['x'])}, {int(coords['y'])})")
            return True
    except:
        pass

    # ====== الطريقة 5: الانتظار ثم النقر (للأزرار الديناميكية) ======
    try:
        # انتظار أن يصبح الزر قابلاً للنقر (enabled)
        await page.wait_for_selector('button:has-text("Start Lab"):not([disabled])', timeout=10000)

        # محاولة النقر مع retry
        for i in range(3):
            try:
                await page.click('button:has-text("Start Lab")', timeout=5000)
                send_tg(f"✅ تم النقر (Retry {i+1})")
                return True
            except:
                await asyncio.sleep(1)
    except:
        pass

    # ====== الطريقة 6: البحث في iframe ======
    try:
        for frame in page.frames:
            try:
                btn = frame.locator('button:has-text("Start Lab")').first
                if await btn.count() > 0 and await btn.is_visible():
                    await btn.click(force=True)
                    send_tg("✅ تم النقر (Inside iframe)")
                    return True
            except:
                continue
    except:
        pass

    send_tg("❌ جميع المحاولات فشلت")
    return False

async def handle_recaptcha(page):
    """معالجة reCAPTCHA"""
    try:
        await asyncio.sleep(2)

        for frame in page.frames:
            if "recaptcha/api2/anchor" in frame.url:
                send_tg("🤖 كابتشا detected")
                try:
                    await frame.evaluate("document.querySelector('.recaptcha-checkbox-border').click()")
                    await asyncio.sleep(5)
                except:
                    pass

                for f in page.frames:
                    if "api2/bframe" in f.url:
                        try:
                            await f.evaluate("document.querySelector('#solver-button').click()")
                            await asyncio.sleep(15)
                        except:
                            pass
                return True
    except:
        pass
    return False

async def run():
    send_tg("🚀 بدء المهمة v3...")
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
                "--window-size=1366,768"
            ]
        )

        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()

        try:
            send_tg("🌐 فتح صفحة اللاب...")
            await page.goto(LAB_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)

            await page.screenshot(path="lab_page.png", full_page=True)
            send_tg("📸 صفحة اللاب", "lab_page.png")

            clicked = await advanced_click_start_lab(page)

            if clicked:
                await asyncio.sleep(8)
                await handle_recaptcha(page)
                await asyncio.sleep(10)

                # التحقق مما إذا نجح النقر (التحقق من URL أو العناصر)
                current_url = page.url
                if "console.cloud.google.com" in current_url or "task" in (await page.content()).lower():
                    send_tg("✅ اللاب بدأ بنجاح!")
                else:
                    send_tg("⚠️ النقر تم لكن لا يوجد تأكيد")

                await page.screenshot(path="after_start.png", full_page=True)
                send_tg("📸 بعد الضغط", "after_start.png")
            else:
                send_tg("❌ فشل النقر")

            await page.screenshot(path="final.png", full_page=True)
            send_tg(f"🏁 انتهت\n🔗 {page.url}", "final.png")

        except Exception as e:
            send_tg(f"❌ خطأ: {str(e)[:200]}")
            await page.screenshot(path="error.png", full_page=True)
            send_tg("📸 لقطة الخطأ", "error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
