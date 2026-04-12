import asyncio
import os
import zipfile
import requests
import re
from playwright.async_api import async_playwright

# ========== إعدادات التيليجرام ==========
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
# =====================================

BASE_URL = "https://www.skills.google/"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

MY_COOKIES = [
    {"domain": ".skills.google", "name": "_ga", "value": "GA1.1.1438878037.1772447126", "path": "/"},
    {"domain": ".skills.google", "name": "_ga_2X30ZRBDSG", "value": "GS2.1.s1775996404$o97$g1$t1775996563$j32$l0$h0", "path": "/"},
    {"domain": "www.skills.google", "name": "_cvl-4_1_14_session", "value": "lQa%2FMnKdErx31nYRawt27XpphO7RO1Mod3%2FCk8T6PqZfkPZohBUhjBqhs2Mw1GIO229gr0KDHGkAp%2F9o7Blffpj%2BNy7YVlSwMKrQX3%2B0RxdyBzB0LU%2BFdcq5wLCPFWUPMhJNMngGjgVjse8JNXc1BO1j2FUpFQqvzAVGdPUShDJMshUZOva39naRS%2BVT%2BpBdaPE0I%2FgjsG6fC6KFeGqADXbUOQ36JiZQkoXYIjuKCxrOKwyaLKj7fFRebXiBduQKQIH3JK8bvcn0LkvK8BuvZ262zjAku4%2FkzRdFKfsfQMXrZStwGytxy1dqm%2FoQ6Lut8s9fnFVTGGcYIoJoxwba0Yx653S2FCemxd3GSCCqfGuNfuzRfNSCjsYvAeUmPdkQzepE80F3hbK15UUyM%2B2Puh3e4e%2FoovbnYf0xLZFGrxSpTcgJ5zb1FElGZ9LNFypWppJjbPlIySkS6X00pjko3fzmpi2TmUHvdBfPbn7ZmJbQ%2Fa8mQzvispzCN8GaAavsOZ%2FsD6xOt0%2FukYWX4oyXfRQg8AP8iZvYkj1iOvsbagPMKjp7utfL9DzDJ5n7LorhayjfSh9XLi1us38cm%2Fu8fzdbvLJn0DJ7koAN2V8V2KKLiGrU2H3e2z4pAFvTAmFENKac3LdIOOs2oNNj2Z8yF0iEnprV%2FzPeOb7eCcvFU66A6qb3f4SgUOTFVchEXizCrTx0%2FvdEQhoQG%2Boc3WXvnYtDbpPIuyt0BJSUda0e63hfWvQnww7DjHcdLtchLMoGYyOW0UktBRGkG3s%3D--TF35bd8CfnDqO%2BYr--Bp220SPOMrUj1y6NmvAiVw%3D%3D", "path": "/", "secure": True, "httpOnly": True},
    {"domain": "www.skills.google", "name": "user.id", "value": "eyJfcmFpbHMiOnsibWVzc2FnZSI6Ik1UTTNOVE13TmpJMyIsImV4cCI6bnVsbCwicHVyIjoiY29va2llLnVzZXIuaWQifX0%3D--3706d9f3abb091776145342b4e9be6e645941d44", "path": "/", "secure": True}
]

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
    zip_p = "buster-main.zip"
    dest = "ext_folder"
    if os.path.exists(zip_p):
        with zipfile.ZipFile(zip_p, 'r') as z: z.extractall(dest)
        for r, d, f in os.walk(dest):
            if "manifest.json" in f: return os.path.abspath(r)
    return os.path.abspath(dest)

async def click_button_by_text_anywhere(page, text, exact=False, timeout_loop=40):
    pattern = re.compile(rf"^\s*{re.escape(text)}\s*$", re.I) if exact else re.compile(re.escape(text), re.I)
    for _ in range(timeout_loop):
        for target in [page] + list(page.frames):
            try:
                # محاولة الضغط عبر Playwright API
                btns = target.get_by_role("button", name=pattern)
                count = await btns.count()
                if count > 0:
                    btn = btns.first
                    if await btn.is_visible():
                        await btn.click(timeout=3000, force=True)
                        return True
                
                # محاولة الضغط عبر JavaScript كخطة بديلة (Fallback)
                success = await target.evaluate(f"""(txt) => {{
                    const elements = Array.from(document.querySelectorAll('button, a, .ql-button'));
                    const target = elements.find(el => el.innerText.toLowerCase().includes(txt.toLowerCase()));
                    if (target) {{
                        target.click();
                        return true;
                    }}
                    return false;
                }}""", text)
                if success: return True
            except: pass
        await asyncio.sleep(1)
    return False

async def run():
    send_tg("⚙️ جاري بدء تنفيذ السكريبت...")
    ext_path = await get_ext()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"
            ]
        )
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()

        try:
            # الدخول لصفحة اللاب
            await page.goto(LAB_URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
            
            await page.screenshot(path="start_page.png")
            send_tg("📸 تم فتح صفحة اللاب. جاري محاولة البدء...", "start_page.png")

            # استخدام الدالة "الجوكر" التي تعمل معك في سورس VLESS
            clicked = await click_button_by_text_anywhere(page, "Start Lab")
            if not clicked:
                clicked = await click_button_by_text_anywhere(page, "بدء")
            
            if clicked:
                send_tg("✅ تم الضغط على زر البدء.")
                await asyncio.sleep(8)
                
                # التعامل مع الكبتشا بواسطة الإضافة
                for f in page.frames:
                    if "api2/anchor" in f.url:
                        await f.click(".recaptcha-checkbox-border")
                        await asyncio.sleep(3)
                    if "api2/bframe" in f.url:
                        await f.locator("#solver-button").click()
                        await asyncio.sleep(15)
            else:
                send_tg("❌ فشل العثور على زر البدء.")
                await page.screenshot(path="failed.png")
                send_tg("📸 صورة الفشل:", "failed.png")

            await asyncio.sleep(10)
            await page.screenshot(path="final.png")
            send_tg(f"🏁 اكتمال. الرابط: {page.url}", "final.png")

        except Exception as e:
            send_tg(f"❌ حدث خطأ: {str(e)[:200]}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
    return os.path.abspath(r)
    return os.path.abspath(dest)

async def get_page_html(page):
    """الحصول على HTML الكامل للصفحة"""
    try:
        html = await page.content()
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(html)
        return html[:50000]  # أول 50KB
    except Exception as e:
        return f"Error: {e}"

async def find_start_lab_deep(page):
    """بحث عميق عن زر Start Lab"""
    
    # البحث في الصفحة الرئيسية وكل الـ frames
    search_results = await page.evaluate("""
        () => {
            const results = [];
            
            // دالة للبحث في أي عنصر
            const searchElement = (el, depth = 0) => {
                if (depth > 10) return;
                
                const text = (el.innerText || el.textContent || el.value || '').trim();
                const tag = el.tagName?.toLowerCase();
                const rect = el.getBoundingClientRect?.();
                
                // البحث عن نص Start Lab
                if (text.toLowerCase().includes('start lab') || 
                    text.toLowerCase().includes('launch lab') ||
                    text.toLowerCase().includes('resume lab') ||
                    text.toLowerCase().includes('begin lab')) {
                    
                    results.push({
                        tag: tag,
                        text: text.substring(0, 100),
                        id: el.id,
                        class: el.className,
                        role: el.getAttribute('role'),
                        clickable: el.tagName === 'BUTTON' || 
                                   el.tagName === 'A' || 
                                   el.getAttribute('role') === 'button' ||
                                   el.onclick !== null,
                        visible: rect && rect.width > 0 && rect.height > 0,
                        x: rect?.x,
                        y: rect?.y,
                        width: rect?.width,
                        height: rect?.height,
                        path: getPath(el)
                    });
                }
                
                // البحث في الأبناء
                for (const child of el.children) {
                    searchElement(child, depth + 1);
                }
            };
            
            // الحصول على مسار العنصر
            const getPath = (el) => {
                const path = [];
                while (el && el.tagName) {
                    let selector = el.tagName.toLowerCase();
                    if (el.id) selector += '#' + el.id;
                    else if (el.className) selector += '.' + el.className.split(' ')[0];
                    path.unshift(selector);
                    el = el.parentElement;
                }
                return path.join(' > ');
            };
            
            // البحث في body
            searchElement(document.body);
            
            // البحث في Shadow DOM
            const searchShadow = (root) => {
                if (!root) return;
                const walker = document.createTreeWalker(
                    root, 
                    NodeFilter.SHOW_ELEMENT,
                    null,
                    false
                );
                let node;
                while (node = walker.nextNode()) {
                    if (node.shadowRoot) {
                        searchElement(node.shadowRoot);
                        searchShadow(node.shadowRoot);
                    }
                }
            };
            searchShadow(document.body);
            
            return results;
        }
    """)
    
    return search_results

async def click_by_javascript(page, element_info):
    """النقر على عنصر باستخدام JavaScript"""
    
    success = await page.evaluate(f"""
        () => {{
            // البحث بالنص
            const allElements = document.querySelectorAll('*');
            for (const el of allElements) {{
                const text = (el.innerText || el.textContent || '').toLowerCase();
                if (text.includes('start lab')) {{
                    // التمرير والنقر
                    el.scrollIntoView({{block: 'center', behavior: 'instant'}});
                    
                    // محاكاة جميع أحداث النقر
                    const events = ['mousedown', 'mouseup', 'click'];
                    for (const eventType of events) {{
                        const event = new MouseEvent(eventType, {{
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }});
                        el.dispatchEvent(event);
                    }}
                    
                    // النقر الأصلي
                    if (el.click) el.click();
                    
                    // إذا كان رابط
                    if (el.tagName === 'A' && el.href) {{
                        window.location.href = el.href;
                    }}
                    
                    return {{success: true, tag: el.tagName, text: el.innerText?.substring(0, 50)}};
                }}
            }}
            return {{success: false}};
        }}
    """)
    
    return success.get('success', False)

async def click_start_lab_final(page):
    """الطريقة النهائية للنقر على Start Lab"""
    
    send_tg("🔍 البحث العميق عن Start Lab...")
    
    # 1. البحث العميق
    results = await find_start_lab_deep(page)
    
    if not results:
        send_tg("❌ لم يتم العثور على أي عنصر يحتوي على 'Start Lab'")
        return False
    
    # عرض النتائج
    msg = f"🔍 وجدت {len(results)} عنصر:\n"
    for i, r in enumerate(results[:5]):
        status = "🟢" if r['clickable'] else "🔴"
        msg += f"\n{status} {i+1}. <{r['tag']}> '{r['text'][:40]}'"
        msg += f"\n   📍 ({int(r['x'])}, {int(r['y'])}) | visible: {r['visible']}"
    send_tg(msg[:4000])
    
    # 2. محاولة النقر على أول عنصر قابل للنقر
    for element in results:
        if element['clickable'] and element['visible']:
            try:
                # محاولة النقر بالـ Playwright
                if element['x'] is not None and element['y'] is not None:
                    await page.mouse.click(
                        element['x'] + element['width']/2, 
                        element['y'] + element['height']/2
                    )
                    send_tg(f"✅ تم النقر بالإحداثيات على: {element['text'][:30]}")
                    return True
            except Exception as e:
                send_tg(f"⚠️ فشل النقر بالإحداثيات: {e}")
    
    # 3. محاولة JavaScript
    send_tg("🔄 محاولة JavaScript...")
    if await click_by_javascript(page, results[0]):
        return True
    
    return False

async def handle_recaptcha(page):
    """معالجة reCAPTCHA"""
    try:
        await asyncio.sleep(2)
        
        for frame in page.frames:
            if "recaptcha" in frame.url:
                send_tg("🤖 reCAPTCHA detected")
                await asyncio.sleep(10)  # انتظار الـ extension
                return True
    except:
        pass
    return False

async def run():
    send_tg("🚀 بدء المهمة v4 (بحث عميق)...")
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
            
            # حفظ HTML للتحليل
            html = await get_page_html(page)
            send_tg(f"📄 HTML saved ({len(html)} chars)")
            
            # البحث العميق والنقر
            clicked = await click_start_lab_final(page)

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
            send_tg(f"❌ خطأ: {str(e)[:400]}")
            await page.screenshot(path="error.png", full_page=True)
            send_tg("📸 لقطة الخطأ", "error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
