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

async def diagnose_buttons(page):
    """تشخيص: طباعة جميع الأزرار المرئية"""
    try:
        buttons_info = await page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button');
                return Array.from(buttons).map((btn, i) => {
                    const rect = btn.getBoundingClientRect();
                    const style = window.getComputedStyle(btn);
                    return {
                        index: i,
                        text: btn.innerText || btn.textContent || '',
                        class: btn.className,
                        id: btn.id,
                        visible: style.display !== 'none' && style.visibility !== 'hidden',
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        bgColor: style.backgroundColor,
                        clickable: btn.disabled === false
                    };
                });
            }
        """)

        msg = "📊 الأزرار الموجودة:\n"
        for btn in buttons_info:
            if btn['visible'] and btn['text'].strip():
                msg += f"\n{i+1}. '{btn['text'][:30]}' @ ({int(btn['x'])}, {int(btn['y'])}) - {btn['bgColor']}"

        send_tg(msg[:4000])  # Telegram limit
        return buttons_info
    except Exception as e:
        send_tg(f"⚠️ خطأ في التشخيص: {e}")
        return []

async def click_start_lab_all_methods(page):
    """جميع طرق Playwright للنقر على زر Start Lab"""

    # أولاً: التشخيص
    await diagnose_buttons(page)

    send_tg("🔍 البحث عن زر Start Lab بجميع الطرق...")

    # الطريقة 1: المحدد الدقيق مع انتظار طويل
    try:
        btn = page.locator('button.ql-button--primary:has-text("Start Lab")').first
        await btn.wait_for(state="visible", timeout=15000)

        # التحقق من أن الزر يستقبل النقرات
        box = await btn.bounding_box()
        if box:
            send_tg(f"✅ الزر موجود في ({int(box['x'])}, {int(box['y'])})")

            # محاولة 1a: النقر العادي
            try:
                await btn.click(timeout=10000)
                send_tg("✅ تم النقر (طريقة 1: click)")
                return True
            except:
                pass

            # محاولة 1b: النقر مع force
            try:
                await btn.click(force=True, timeout=10000)
                send_tg("✅ تم النقر (طريقة 2: force click)")
                return True
            except:
                pass

            # محاولة 1c: النقر بالإحداثيات
            try:
                x = box['x'] + box['width'] / 2
                y = box['y'] + box['height'] / 2
                await page.mouse.click(x, y)
                send_tg("✅ تم النقر (طريقة 3: mouse coordinates)")
                return True
            except:
                pass
    except Exception as e:
        send_tg(f"⚠️ الطريقة 1 فشلت: {str(e)[:100]}")

    # الطريقة 2: استخدام JavaScript evaluate
    try:
        result = await page.evaluate("""
            () => {
                // البحث عن الزر بالنص الدقيق
                const buttons = Array.from(document.querySelectorAll('button'));
                const targetBtn = buttons.find(btn => {
                    const text = (btn.innerText || btn.textContent || '').trim().toLowerCase();
                    return text === 'start lab' || text.includes('start lab');
                });

                if (targetBtn) {
                    // التمرير والنقر
                    targetBtn.scrollIntoView({block: 'center', behavior: 'smooth'});

                    // محاكاة النقر الكامل
                    const mousedown = new MouseEvent('mousedown', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    const click = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    const mouseup = new MouseEvent('mouseup', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });

                    targetBtn.dispatchEvent(mousedown);
                    targetBtn.dispatchEvent(click);
                    targetBtn.dispatchEvent(mouseup);

                    // كمحاولة إضافية
                    targetBtn.click();

                    return {success: true, text: targetBtn.innerText};
                }
                return {success: false, reason: 'Button not found'};
            }
        """)

        if result and result.get('success'):
            send_tg(f"✅ تم النقر (طريقة 4: JavaScript) - {result.get('text')}")
            return True
    except Exception as e:
        send_tg(f"⚠️ الطريقة 4 فشلت: {str(e)[:100]}")

    # الطريقة 5: البحث في iframe إذا وجد
    try:
        for frame in page.frames:
            try:
                btn = frame.locator('button:has-text("Start Lab")').first
                if await btn.count() > 0:
                    await btn.click(force=True)
                    send_tg("✅ تم النقر (طريقة 5: inside iframe)")
                    return True
            except:
                continue
    except:
        pass

    # الطريقة 6: استخدام keyboard (Tab + Enter)
    try:
        # الذهاب إلى بداية الصفحة ثم الضغط Tab حتى نصل للزر
        await page.keyboard.press("Home")
        for i in range(20):  # 20 محاولة Tab
            await page.keyboard.press("Tab")
            await asyncio.sleep(0.1)
            # التحقق إذا كان الزر النشط هو Start Lab
            active = await page.evaluate("() => document.activeElement.innerText || document.activeElement.textContent")
            if active and "start lab" in active.lower():
                await page.keyboard.press("Enter")
                send_tg("✅ تم النقر (طريقة 6: keyboard Enter)")
                return True
    except:
        pass

    # الطريقة 7: النقر على العنصر الأب (parent)
    try:
        parent = page.locator('button.ql-button--primary:has-text("Start Lab")').locator('..')
        if await parent.count() > 0:
            await parent.first.click(force=True)
            send_tg("✅ تم النقر (طريقة 7: parent element)")
            return True
    except:
        pass

    send_tg("❌ فشلت جميع طرق النقر")
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
    send_tg("🚀 بدء المهمة v2...")
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

            # محاولة النقر بجميع الطرق
            clicked = await click_start_lab_all_methods(page)

            if clicked:
                await asyncio.sleep(8)
                await handle_recaptcha(page)
                await asyncio.sleep(10)
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
