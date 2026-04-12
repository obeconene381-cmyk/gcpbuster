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

async def diagnose_page(page):
    """تشخيص شامل للصفحة"""
    try:
        # الحصول على جميع الأزرار
        buttons_info = await page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button, [role="button"], input[type="submit"]');
                return Array.from(buttons).map((btn, idx) => {
                    const rect = btn.getBoundingClientRect();
                    const style = window.getComputedStyle(btn);
                    return {
                        index: idx,
                        text: (btn.innerText || btn.textContent || btn.value || '').trim(),
                        class: btn.className,
                        id: btn.id,
                        tag: btn.tagName,
                        type: btn.type,
                        visible: style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0,
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        disabled: btn.disabled,
                        clickable: !btn.disabled && style.pointerEvents !== 'none'
                    };
                });
            }
        """)

        msg = "📊 الأزرار المرئية:\n"
        visible_buttons = [b for b in buttons_info if b['visible']]
        for i, btn in enumerate(visible_buttons[:15]):  # أول 15 زر
            status = "🟢" if btn['clickable'] else "🔴"
            msg += f"\n{status} {i+1}. '{btn['text'][:40]}' | class: {btn['class'][:30]}... | ({int(btn['x'])}, {int(btn['y'])})"

        send_tg(msg[:4000])
        return visible_buttons
    except Exception as e:
        send_tg(f"⚠️ خطأ في التشخيص: {e}")
        return []

async def wait_and_find_start_button(page, timeout=30000):
    """البحث عن زر Start Lab مع انتظار"""
    selectors = [
        'button:has-text("Start Lab")',
        'button:has-text("START LAB")',
        'button:has-text("Start lab")',
        'button.ql-button--primary:has-text("Start")',
        'button[class*="primary"]:has-text("Start Lab")',
        'button[data-testid*="start"]',
        '[role="button"]:has-text("Start Lab")',
        'button:has-text("Launch Lab")',
        'button:has-text("Resume Lab")',
        'button:has-text("Begin Lab")',
        '//button[contains(text(), "Start")]',  # XPath
        'button >> text=Start Lab',
    ]
    
    for selector in selectors:
        try:
            if selector.startswith('//'):
                # XPath
                btn = page.locator(f'xpath={selector}')
            else:
                btn = page.locator(selector)
            
            await btn.wait_for(state="visible", timeout=timeout // len(selectors))
            count = await btn.count()
            if count > 0:
                send_tg(f"✅ وجدت الزر بالـ selector: {selector[:50]}")
                return btn.first
        except:
            continue
    
    return None

async def click_start_lab_robust(page):
    """طريقة قوية للنقر على زر Start Lab"""
    
    # 1. الانتظار والبحث عن الزر
    send_tg("🔍 البحث عن زر Start Lab...")
    btn = await wait_and_find_start_button(page)
    
    if not btn:
        send_tg("❌ لم يتم العثور على الزر بالـ selectors القياسية")
        return False
    
    # 2. التمرير إلى الزر
    try:
        await btn.scroll_into_view_if_needed()
        await asyncio.sleep(1)
    except:
        pass
    
    # 3. الحصول على معلومات الزر
    try:
        box = await btn.bounding_box()
        if box:
            send_tg(f"📍 الزر في: x={int(box['x'])}, y={int(box['y'])}, w={int(box['width'])}, h={int(box['height'])}")
    except:
        pass
    
    # 4. محاولات النقر المتعددة
    methods = [
        ("click", lambda: btn.click(timeout=10000)),
        ("click force", lambda: btn.click(force=True, timeout=10000)),
        ("dispatchEvent", lambda: btn.dispatch_event("click")),
    ]
    
    for method_name, click_action in methods:
        try:
            await click_action()
            send_tg(f"✅ تم النقر بنجاح بطريقة: {method_name}")
            await asyncio.sleep(3)
            return True
        except Exception as e:
            send_tg(f"⚠️ فشلت طريقة {method_name}: {str(e)[:100]}")
            continue
    
    # 5. النقر بالإحداثيات
    try:
        box = await btn.bounding_box()
        if box and box['width'] > 0:
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            await page.mouse.click(x, y)
            send_tg("✅ تم النقر بالإحداثيات")
            return True
    except Exception as e:
        send_tg(f"⚠️ فشل النقر بالإحداثيات: {e}")
    
    # 6. JavaScript click
    try:
        result = await page.evaluate("""
            () => {
                const findButton = () => {
                    // البحث بعدة طرق
                    const selectors = [
                        'button.ql-button--primary',
                        'button[class*="primary"]',
                        'button[data-testid*="start"]',
                        'button'
                    ];
                    
                    for (const sel of selectors) {
                        const btns = document.querySelectorAll(sel);
                        for (const btn of btns) {
                            const text = (btn.innerText || btn.textContent || '').toLowerCase();
                            if (text.includes('start lab') || text.includes('launch lab') || text.includes('resume lab')) {
                                return btn;
                            }
                        }
                    }
                    return null;
                };
                
                const btn = findButton();
                if (btn) {
                    btn.scrollIntoView({block: 'center', behavior: 'instant'});
                    
                    // محاكاة النقر الكامل
                    ['mousedown', 'click', 'mouseup'].forEach(type => {
                        btn.dispatchEvent(new MouseEvent(type, {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }));
                    });
                    
                    // click() الأصلي
                    btn.click();
                    
                    return {success: true, text: btn.innerText};
                }
                return {success: false};
            }
        """)
        
        if result.get('success'):
            send_tg(f"✅ تم النقر بـ JavaScript: {result.get('text')}")
            return True
    except Exception as e:
        send_tg(f"⚠️ فشل JavaScript: {e}")
    
    return False

async def handle_recaptcha(page):
    """معالجة reCAPTCHA"""
    try:
        await asyncio.sleep(2)
        
        # البحث عن iframe الكابتشا
        captcha_frame = None
        for frame in page.frames:
            if "recaptcha" in frame.url:
                captcha_frame = frame
                break
        
        if captcha_frame:
            send_tg("🤖 reCAPTCHA detected")
            
            # الانتظار قليلاً للـ extension يعمل
            await asyncio.sleep(10)
            
            # التحقق إذا تم الحل
            try:
                checkbox = captcha_frame.locator('.recaptcha-checkbox-checked')
                if await checkbox.count() > 0:
                    send_tg("✅ reCAPTCHA تم حلها")
                    return True
            except:
                pass
                
    except Exception as e:
        send_tg(f"⚠️ خطأ في معالجة الكابتشا: {e}")
    
    return False

async def run():
    send_tg("🚀 بدء المهمة v3 (مصححة)...")
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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0.36"
        )

        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()

        try:
            send_tg("🌐 فتح صفحة اللاب...")
            await page.goto(LAB_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)

            await page.screenshot(path="lab_page.png", full_page=True)
            send_tg("📸 صفحة اللاب مفتوحة", "lab_page.png")
            
            # تشخيص الصفحة
            await diagnose_page(page)

            # محاولة النقر
            clicked = await click_start_lab_robust(page)

            if clicked:
                await asyncio.sleep(8)
                await handle_recaptcha(page)
                await asyncio.sleep(10)
                await page.screenshot(path="after_start.png", full_page=True)
                send_tg("📸 بعد الضغط", "after_start.png")
            else:
                send_tg("❌ فشل النقر على الزر")
                # محاولة أخيرة: إعادة تحميل الصفحة والمحاولة مرة أخرى
                send_tg("🔄 إعادة المحاولة بعد إعادة التحميل...")
                await page.reload(wait_until="networkidle")
                await asyncio.sleep(5)
                clicked = await click_start_lab_robust(page)
                if clicked:
                    send_tg("✅ نجحت المحاولة الثانية")

            await page.screenshot(path="final.png", full_page=True)
            send_tg(f"🏁 انتهت\n🔗 {page.url}", "final.png")

        except Exception as e:
            send_tg(f"❌ خطأ: {str(e)[:400]}")
            await page.screenshot(path="error.png", full_page=True)
            send_tg("📸 لقطة الخطأ", "error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
