import asyncio
import os
import zipfile
import requests
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ========== إعدادات التيليجرام ==========
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
# =====================================

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

async def robust_click_start_lab(page):
    """طريقة قوية للنقر على زر Start Lab"""
    send_tg("🔍 جاري البحث عن زر Start Lab...")

    # انتظار إضافي للتأكد من تحميل الصفحة بالكامل
    await asyncio.sleep(5)

    # محاولة 1: استخدام JavaScript للبحث والنقر
    try:
        result = await page.evaluate("""
            () => {
                // البحث عن الزر بجميع الطرق الممكنة
                const buttons = Array.from(document.querySelectorAll('button, a, input[type="button"], input[type="submit"], [role="button"]'));

                // البحث بالنص
                let btn = buttons.find(b => {
                    const text = (b.innerText || b.textContent || b.value || '').toLowerCase();
                    return text.includes('start lab') || text.includes('start') || text.includes('lab');
                });

                // البحث بالكلاسات
                if (!btn) {
                    btn = document.querySelector('.ql-button--primary') || 
                          document.querySelector('.start-lab-button') ||
                          document.querySelector('[data-testid="start-lab-button"]') ||
                          document.querySelector('button.ql-button') ||
                          document.querySelector('button.mdc-button--raised');
                }

                // البحث باللون (الأزرار الخضراء عادةً)
                if (!btn) {
                    const greenBtns = buttons.filter(b => {
                        const style = window.getComputedStyle(b);
                        const bg = style.backgroundColor;
                        return bg.includes('rgb(0, 128') || bg.includes('rgb(0, 200') || bg.includes('green') || bg.includes('rgb(76, 175');
                    });
                    if (greenBtns.length > 0) btn = greenBtns[0];
                }

                if (btn) {
                    // التمرير إلى الزر
                    btn.scrollIntoView({behavior: 'smooth', block: 'center'});

                    // محاكاة النقر الكامل (mousedown, click, mouseup)
                    const clickEvent = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    btn.dispatchEvent(clickEvent);

                    // كمحاولة إضافية، استدعاء click()
                    btn.click();

                    return {success: true, text: btn.innerText || btn.textContent};
                }
                return {success: false, reason: 'Button not found'};
            }
        """)

        if result and result.get('success'):
            send_tg(f"✅ تم النقر على الزر: {result.get('text', 'Start Lab')}")
            return True
    except Exception as e:
        send_tg(f"⚠️ فشلت المحاولة 1: {str(e)[:100]}")

    # محاولة 2: استخدام Playwright مع انتظار طويل
    try:
        # انتظار الزر حتى يكون مرئياً
        await page.wait_for_selector('button:has-text("Start Lab")', state="visible", timeout=10000)

        # النقر مع force=True لتجاوز أي overlay
        await page.click('button:has-text("Start Lab")', force=True, timeout=10000)
        send_tg("✅ تم النقر باستخدام Playwright force click")
        return True
    except:
        pass

    # محاولة 3: النقر بالإحداثيات
    try:
        # الحصول على موقع الزر
        box = await page.locator('button:has-text("Start Lab")').bounding_box()
        if box:
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            await page.mouse.click(x, y)
            send_tg("✅ تم النقر بالإحداثيات")
            return True
    except:
        pass

    # محاولة 4: البحث في Shadow DOM
    try:
        result = await page.evaluate("""
            () => {
                function findButtonInShadowDOM(root) {
                    const buttons = Array.from(root.querySelectorAll('button'));
                    const found = buttons.find(b => b.textContent.toLowerCase().includes('start'));
                    if (found) return found;

                    const allElements = root.querySelectorAll('*');
                    for (const el of allElements) {
                        if (el.shadowRoot) {
                            const found = findButtonInShadowDOM(el.shadowRoot);
                            if (found) return found;
                        }
                    }
                    return null;
                }

                const btn = findButtonInShadowDOM(document);
                if (btn) {
                    btn.click();
                    return {success: true};
                }
                return {success: false};
            }
        """)
        if result and result.get('success'):
            send_tg("✅ تم النقر داخل Shadow DOM")
            return True
    except:
        pass

    send_tg("❌ فشلت جميع محاولات النقر")
    return False

async def handle_recaptcha(page):
    """معالجة reCAPTCHA"""
    try:
        # انتظار قصير لظهور الكابتشا
        await asyncio.sleep(2)

        recaptcha_frame = None
        for frame in page.frames:
            if "recaptcha/api2/anchor" in frame.url:
                recaptcha_frame = frame
                break

        if not recaptcha_frame:
            return False

        send_tg("🤖 تم اكتشاف reCAPTCHA")

        # النقر على checkbox باستخدام JavaScript
        try:
            await recaptcha_frame.evaluate("""
                () => {
                    const checkbox = document.querySelector('.recaptcha-checkbox-border');
                    if (checkbox) {
                        checkbox.click();
                        return true;
                    }
                    return false;
                }
            """)
            send_tg("✅ تم النقر على checkbox")
            await asyncio.sleep(5)
        except:
            pass

        # التحقق من التحدي الصوتي
        challenge_frame = None
        for frame in page.frames:
            if "api2/bframe" in frame.url:
                challenge_frame = frame
                break

        if challenge_frame:
            send_tg("🔊 التحدي الصوتي ظهر")
            try:
                # النقر على زر الصوت أولاً
                await challenge_frame.evaluate("""
                    () => {
                        const audioBtn = document.querySelector('#recaptcha-audio-button');
                        if (audioBtn) audioBtn.click();
                    }
                """)
                await asyncio.sleep(2)

                # استخدام Buster
                await challenge_frame.evaluate("""
                    () => {
                        const busterBtn = document.querySelector('#solver-button');
                        if (busterBtn) busterBtn.click();
                    }
                """)
                send_tg("🎯 تم تفعيل Buster")
                await asyncio.sleep(15)
            except Exception as e:
                send_tg(f"⚠️ Buster: {str(e)[:100]}")

        return True
    except:
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
            await asyncio.sleep(5)  # انتظار إضافي للتحميل

            await page.screenshot(path="lab_page.png")
            send_tg("📸 صفحة اللاب مفتوحة", "lab_page.png")

            # محاولة النقر على الزر
            clicked = await robust_click_start_lab(page)

            if clicked:
                send_tg("⏳ انتظار بعد النقر...")
                await asyncio.sleep(8)

                # معالجة الكابتشا إن وجدت
                await handle_recaptcha(page)

                await asyncio.sleep(10)
                await page.screenshot(path="after_click.png", full_page=True)
                send_tg("📸 بعد الضغط", "after_click.png")
            else:
                send_tg("❌ فشل النقر على الزر")

            # الصورة النهائية
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
