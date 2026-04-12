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

async def find_and_click_start_lab_button(page):
    """البحث الدقيق عن زر Start Lab الأخضر فقط"""
    send_tg("🔍 البحث عن زر Start Lab الأخضر...")

    # انتظار تحميل الصفحة بالكامل
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(3)

    # قائمة المحددات الدقيقة لزر Start Lab في Google Skills
    selectors = [
        # محددات CSS محددة للزر الأخضر
        'button.ql-button--primary:has-text("Start Lab")',
        'button.ql-button--primary:has-text("START LAB")',
        'button.ql-button.ql-button--primary:has-text("Start Lab")',
        'button[color="primary"]:has-text("Start Lab")',
        'button.mdc-button--raised:has-text("Start Lab")',

        # محددات XPath دقيقة
        '//button[contains(@class, "ql-button--primary") and contains(text(), "Start Lab")]',
        '//button[contains(@class, "ql-button") and contains(text(), "Start Lab")]',

        # البحث بالخصائص المحددة
        'button[data-testid="start-lab-button"]',
        'button.start-lab-button',

        # البحث في حاوية الـ Lab Setup (الجزء العلوي من الصفحة)
        'div.lab-setup button:has-text("Start Lab")',
        'div.lab-setup-instructions button:has-text("Start Lab")',

        # البحث باللون والنص معاً
        'button:has-text("Start Lab"):has(.ql-button__label)',
        'button:has-text("Start Lab"):not(:has-text("Starter"))',  # تجنب Starter
    ]

    # محاولة 1: استخدام المحددات الدقيقة
    for selector in selectors:
        try:
            if selector.startswith('//'):
                locator = page.locator(f"xpath={selector}")
            else:
                locator = page.locator(selector)

            count = await locator.count()
            if count > 0:
                for i in range(count):
                    btn = locator.nth(i)
                    if await btn.is_visible():
                        text = await btn.text_content()
                        # التحقق الدقيق من النص (يجب أن يحتوي على Start Lab وليس Starter)
                        if text and "start lab" in text.lower() and "starter" not in text.lower():
                            # التحقق من أن الزر في الجزء العلوي من الصفحة (y < 500)
                            box = await btn.bounding_box()
                            if box and box['y'] < 500:  # الزر يجب أن يكون في الأعلى
                                send_tg(f"✅ تم العثور على الزر: {text.strip()}")
                                await btn.scroll_into_view_if_needed()
                                await asyncio.sleep(1)
                                await btn.click(force=True)
                                send_tg("✅ تم النقر على زر Start Lab")
                                return True
        except Exception as e:
            continue

    # محاولة 2: البحث في جميع الأزرار مع فلترة دقيقة
    try:
        buttons = await page.query_selector_all('button')
        for btn in buttons:
            text = await btn.text_content()
            if text:
                text_clean = text.strip().lower()
                # التحقق الدقيق: يجب أن يحتوي على "start lab" بالضبط
                if "start lab" in text_clean and "starter" not in text_clean:
                    # التحقق من اللون (أخضر)
                    style = await btn.evaluate('el => window.getComputedStyle(el).backgroundColor')
                    is_green = any(color in style for color in ['rgb(0, 128', 'rgb(0, 200', 'rgb(76, 175', 'green', 'rgb(34, 139'])

                    # التحقق من الموقع (يجب أن يكون في الأعلى)
                    box = await btn.bounding_box()
                    is_top = box and box['y'] < 400

                    if is_green or is_top:
                        await btn.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        await btn.click()
                        send_tg(f"✅ تم النقر على الزر (طريقة 2): {text.strip()}")
                        return True
    except Exception as e:
        send_tg(f"⚠️ فشلت الطريقة 2: {str(e)[:100]}")

    # محاولة 3: JavaScript للبحث الدقيق
    try:
        result = await page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = btn.innerText || btn.textContent || '';
                    const cleanText = text.trim().toLowerCase();

                    // التحقق الدقيق من النص
                    if (cleanText.includes('start lab') && !cleanText.includes('starter')) {
                        // التحقق من الموقع (يجب أن يكون في الجزء العلوي)
                        const rect = btn.getBoundingClientRect();
                        if (rect.top < 400) {
                            btn.scrollIntoView({block: 'center'});
                            btn.click();
                            return {success: true, text: text};
                        }
                    }
                }
                return {success: false};
            }
        """)
        if result and result.get('success'):
            send_tg(f"✅ تم النقر باستخدام JavaScript: {result.get('text')}")
            return True
    except Exception as e:
        send_tg(f"⚠️ فشلت الطريقة 3: {str(e)[:100]}")

    send_tg("❌ لم يتم العثور على زر Start Lab الأخضر")
    return False

async def handle_recaptcha(page):
    """معالجة reCAPTCHA"""
    try:
        await asyncio.sleep(2)

        for frame in page.frames:
            if "recaptcha/api2/anchor" in frame.url:
                send_tg("🤖 تم اكتشاف reCAPTCHA")
                try:
                    await frame.evaluate("document.querySelector('.recaptcha-checkbox-border').click()")
                    send_tg("✅ تم النقر على checkbox")
                    await asyncio.sleep(5)
                except:
                    pass

                for f in page.frames:
                    if "api2/bframe" in f.url:
                        send_tg("🔊 استخدام Buster...")
                        try:
                            await f.evaluate("document.querySelector('#recaptcha-audio-button').click()")
                            await asyncio.sleep(2)
                            await f.evaluate("document.querySelector('#solver-button').click()")
                            await asyncio.sleep(15)
                        except:
                            pass
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
            send_tg("📸 صفحة اللاب مفتوحة", "lab_page.png")

            clicked = await find_and_click_start_lab_button(page)

            if clicked:
                await asyncio.sleep(8)
                await handle_recaptcha(page)
                await asyncio.sleep(10)
                await page.screenshot(path="after_start.png", full_page=True)
                send_tg("📸 بعد الضغط على Start Lab", "after_start.png")
            else:
                send_tg("❌ فشل في العثور على زر Start Lab")

            await page.screenshot(path="final.png", full_page=True)
            send_tg(f"🏁 المهمة انتهت\n🔗 {page.url}", "final.png")

        except Exception as e:
            send_tg(f"❌ خطأ: {str(e)[:200]}")
            await page.screenshot(path="error.png", full_page=True)
            send_tg("📸 لقطة الخطأ", "error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
