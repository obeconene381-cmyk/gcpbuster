import asyncio
import os
import zipfile
import requests
import re
import shutil
import random
from playwright.async_api import async_playwright

# --- الإعدادات ---
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

BUSTER_COMPILED_URL = "https://github.com/dessant/buster/releases/download/v3.1.0/buster_captcha_solver_for_humans-3.1.0-chrome.zip"

WORKING_PROXY = {
    "server": "http://92.119.128.15:9996",
    "username": "user376353",
    "password": "y3ld6w"
}

MY_COOKIES = [
    {"domain": ".skills.google", "name": "_ga", "value": "GA1.1.1438878037.1772447126", "path": "/"},
    {"domain": "www.skills.google", "name": "_cvl-4_1_14_session", "value": "lQa%2FMnKdErx31nYRawt27XpphO7RO1Mod3%2FCk8T6PqZfkPZohBUhjBqhs2Mw1GIO229gr0KDHGkAp%2F9o7Blffpj%2BNy7YVlSwMKrQX3%2B0RxdyBzB0LU%2BFdcq5wLCPFWUPMhJNMngGjgVjse8JNXc1BO1j2FUpFQqvzAVGdPUShDJMshUZOva39naRS%2BVT%2BpBdaPE0I%2FgjsG6fC6KFeGqADXbUOQ36JiZQkoXYIjuKCxrOKwyaLKj7fFRebXiBduQKQIH3JK8bvcn0LkvK8BuvZ262zjAku4%2FkzRdFKfsfQMXrZStwGytxy1dqm%2FoQ6Lut8s9fnFVTGGcYIoJoxwba0Yx653S2FCemxd3GSCCqfGuNfuzRfNSCjsYvAeUmPdkQzepE80F3hbK15UUyM%2B2Puh3e4e%2FoovbnYf0xLZFGrxSpTcgJ5zb1FElGZ9LNFypWppJjbPlIySkS6X00pjko3fzmpi2TmUHvdBfPbn7ZmJbQ%2Fa8mQzvispzCN8GaAavsOZ%2FsD6xOt0%2FukYWX4oyXfRQg8AP8iZvYkj1iOvsbagPMKjp7utfL9DzDJ5n7LorhayjfSh9XLi1us38cm%2Fu8fzdbvLJn0DJ7koAN2V8V2KKLiGrU2H3e2z4pAFvTAmFENKac3LdIOOs2oNNj2Z8yF0iEnprV%2FzPeOb7eCcvFU66A6qb3f4SgUOTFVchEXizCrTx0%2FvdEQhoQG%2Boc3WXvnYtDbpPIuyt0BJSUda0e63hfWvQnww7DjHcdLtchLMoGYyOW0UktBRGkG3s%3D--TF35bd8CfnDqO%2BYr--Bp220SPOMrUj1y6NmvAiVw%3D%3D", "path": "/", "secure": True, "httpOnly": True},
    {"domain": "www.skills.google", "name": "user.id", "value": "eyJfcmFpbHMiOnsibWVzc2FnZSI6Ik1UTTNOVE13TmpJMyIsImV4cCI6bnVsbCwicHVyIjoiY29va2llLnVzZXIuaWQifX0%3D--3706d9f3abb091776145342b4e9be6e645941d44", "path": "/", "secure": True},
]

def send_tg(msg, img=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if img and os.path.exists(img):
            with open(img, "rb") as f: 
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": msg}, files={"photo": f}, timeout=30)
        else: 
            requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": msg}, timeout=30)
    except: 
        pass

async def setup_compiled_buster():
    ext_dir = os.path.abspath("buster_compiled_ext")
    if os.path.exists(ext_dir): 
        shutil.rmtree(ext_dir)
    os.makedirs(ext_dir)
    zip_path = "buster_ready.zip"
    
    try:
        send_tg("📥 جاري تحميل النسخة الرسمية الجاهزة للإضافة...")
        r = requests.get(BUSTER_COMPILED_URL, timeout=30)
        with open(zip_path, "wb") as f: 
            f.write(r.content)
        
        with zipfile.ZipFile(zip_path, 'r') as z: 
            z.extractall(ext_dir)
            
        os.remove(zip_path)
        send_tg(f"✅ تم تجهيز الإضافة الجاهزة في المسار: {ext_dir}")
        return ext_dir
    except Exception as e:
        send_tg(f"❌ فشل تحميل الإضافة الجاهزة: {e}")
        return None

async def human_click(page, locator):
    try:
        await locator.scroll_into_view_if_needed()
        box = await locator.bounding_box()
        if box:
            x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            await page.mouse.move(x, y, steps=10)
            await asyncio.sleep(0.2)
            await page.mouse.down()
            await asyncio.sleep(0.15)
            await page.mouse.up()
            return True
        await locator.click(delay=200)
        return True
    except: 
        return False

async def dismiss_credits_modal(page):
    try:
        btn = page.get_by_role("button", name=re.compile(r"Dismiss", re.I))
        if await btn.count() > 0 and await btn.first.is_visible():
            await btn.first.click()
            send_tg("✅ تم العثور على نافذة Credits Expiring وإغلاقها.")
            await asyncio.sleep(2)
            return True
            
        text_btn = page.locator("text=Dismiss")
        if await text_btn.count() > 0 and await text_btn.first.is_visible():
            await text_btn.first.click()
            send_tg("✅ تم إغلاق نافذة Credits Expiring.")
            await asyncio.sleep(2)
            return True
    except Exception as e:
        pass
    return False

async def click_start_lab_button(page):
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)
    for _ in range(30):
        try:
            btn = page.get_by_role("button", name=pattern).first
            if await btn.is_visible():
                await btn.click(force=True)
                send_tg("✅ تم الضغط على Start Lab")
                return True
        except: 
            pass
        await asyncio.sleep(1)
    return False

async def click_captcha_checkbox(page):
    send_tg("🤛 البحث عن مربع الكابتشا...")
    await asyncio.sleep(3)
    iframes = await page.locator('iframe[title*="reCAPTCHA"]').all()
    for iframe in iframes:
        try:
            frame_content = iframe.content_frame
            checkbox = frame_content.locator('.recaptcha-checkbox-border').first
            if await checkbox.is_visible():
                await human_click(page, checkbox)
                send_tg("✅ تم الضغط على المربع")
                return True
        except: 
            continue
    return False

# ===============================================
# 🔥 جميع طرق الضغط على Buster 🔥
# ===============================================

async def method_1_shadow_dom_click(page):
    """الطريقة 1: البحث داخل Shadow DOM"""
    send_tg("🎯 الطريقة 1: Shadow DOM Click")
    
    try:
        challenge_iframe = page.frame_locator('iframe[src*="recaptcha/api2/bframe"]').first
        
        audio_btn = challenge_iframe.locator('#recaptcha-audio-button, .rc-button-audio')
        if await audio_btn.is_visible():
            await audio_btn.click()
            await asyncio.sleep(2)
            send_tg("🔊 تم التحويل للصوت")
        
        buster_btn = challenge_iframe.locator('button[title*="Buster"], button[class*="buster"], div[class*="buster"]').first
        
        if await buster_btn.is_visible(timeout=5000):
            await buster_btn.click()
            send_tg("✅ تم الضغط على Buster (Shadow DOM)")
            await asyncio.sleep(8)
            
            verify_btn = challenge_iframe.locator('#recaptcha-verify-button')
            if await verify_btn.is_visible():
                await verify_btn.click()
            
            return True
    except Exception as e:
        send_tg(f"❌ فشلت الطريقة 1: {e}")
    
    await page.screenshot(path="method1_shadow_dom.png")
    send_tg("📸 نتيجة الطريقة 1:", "method1_shadow_dom.png")
    return False

async def method_2_keyboard_shortcut(page):
    """الطريقة 2: اختصار لوحة المفاتيح"""
    send_tg("🎯 الطريقة 2: Keyboard Shortcut")
    
    try:
        iframe = page.frame_locator('iframe[src*="recaptcha/api2/bframe"]').first
        await iframe.locator('body').click()
        await asyncio.sleep(1)
        
        shortcuts = ['Control+Shift+KeyS', 'Control+Shift+KeyA', 'Alt+Shift+KeyS', 'Control+Period']
        
        for shortcut in shortcuts:
            await page.keyboard.press(shortcut)
            send_tg(f"⌨️ جربت: {shortcut}")
            await asyncio.sleep(3)
            
            if await page.locator('.recaptcha-checkbox-checked').is_visible():
                send_tg(f"✅ نجح الاختصار: {shortcut}")
                return True
        
    except Exception as e:
        send_tg(f"❌ فشلت الطريقة 2: {e}")
    
    await page.screenshot(path="method2_keyboard.png")
    send_tg("📸 نتيجة الطريقة 2:", "method2_keyboard.png")
    return False

async def method_3_js_injection(page):
    """الطريقة 3: حقن JavaScript"""
    send_tg("🎯 الطريقة 3: JavaScript Injection")
    
    script = """
    () => {
        const audioBtn = document.querySelector('#recaptcha-audio-button, .rc-button-audio');
        if (audioBtn) audioBtn.click();
        
        const iframes = document.querySelectorAll('iframe');
        for (let iframe of iframes) {
            try {
                const doc = iframe.contentDocument || iframe.contentWindow.document;
                const buster = doc.querySelector('button[class*="buster"], [data-buster], button[title*="solve"]');
                if (buster) {
                    buster.click();
                    return 'found_in_iframe';
                }
            } catch(e) {}
        }
        
        const allElements = document.querySelectorAll('*');
        for (let el of allElements) {
            if (el.shadowRoot) {
                const buster = el.shadowRoot.querySelector('button[class*="buster"], [class*="solver"]');
                if (buster) {
                    buster.click();
                    return 'found_in_shadow';
                }
            }
        }
        
        window.postMessage({type: 'BUSTER_SOLVE'}, '*');
        return 'not_found';
    }
    """
    
    try:
        result = await page.evaluate(script)
        send_tg(f"🔍 نتيجة JS: {result}")
        await asyncio.sleep(8)
        
        if await page.locator('.recaptcha-checkbox-checked').is_visible():
            send_tg("✅ نجحت الطريقة 3")
            return True
            
    except Exception as e:
        send_tg(f"❌ فشلت الطريقة 3: {e}")
    
    await page.screenshot(path="method3_js.png")
    send_tg("📸 نتيجة الطريقة 3:", "method3_js.png")
    return False

async def method_4_dynamic_coordinates(page):
    """الطريقة 4: إحداثيات ديناميكية"""
    send_tg("🎯 الطريقة 4: Dynamic Coordinates")
    
    try:
        iframe_el = page.locator('iframe[src*="recaptcha/api2/bframe"]').first
        await iframe_el.wait_for(state='visible', timeout=10000)
        
        box = await iframe_el.bounding_box()
        if not box:
            return False
        
        frame = iframe_el.content_frame
        audio_btn = frame.locator('#recaptcha-audio-button')
        
        if await audio_btn.is_visible():
            await audio_btn.click()
            await asyncio.sleep(2)
            
            box = await iframe_el.bounding_box()
            
            positions = [(0.85, 0.75), (0.90, 0.70), (0.80, 0.80), (0.88, 0.72)]
            
            for i, (px, py) in enumerate(positions):
                x = box['x'] + (box['width'] * px)
                y = box['y'] + (box['height'] * py)
                
                await page.mouse.move(x, y)
                await page.screenshot(path=f"method4_pos{i}.png")
                send_tg(f"📍 تجربة الموقع {i+1}: {x:.0f},{y:.0f}", f"method4_pos{i}.png")
                
                await page.mouse.click(x, y)
                await asyncio.sleep(5)
                
                if await page.locator('.recaptcha-checkbox-checked').is_visible():
                    send_tg(f"✅ نجحت الطريقة 4 عند الموقع {i+1}")
                    return True
        
    except Exception as e:
        send_tg(f"❌ فشلت الطريقة 4: {e}")
    
    await page.screenshot(path="method4_final.png")
    send_tg("📸 نتيجة الطريقة 4:", "method4_final.png")
    return False

async def method_5_visual_detection(page):
    """الطريقة 5: كشف بصري باللون الأصفر"""
    send_tg("🎯 الطريقة 5: Visual Yellow Detection")
    
    try:
        await page.screenshot(path="full_page.png", full_page=False)
        
        await page.evaluate("""
            () => {
                const iframes = document.querySelectorAll('iframe[src*="recaptcha"]');
                iframes.forEach((iframe, idx) => {
                    const rect = iframe.getBoundingClientRect();
                    const marker = document.createElement('div');
                    marker.style.cssText = `
                        position: fixed;
                        left: ${rect.left}px;
                        top: ${rect.top}px;
                        width: ${rect.width}px;
                        height: ${rect.height}px;
                        border: 3px solid red;
                        z-index: 999999;
                        pointer-events: none;
                    `;
                    document.body.appendChild(marker);
                });
            }
        """)
        
        await page.screenshot(path="method5_marked.png")
        send_tg("📸 علامات على مناطق reCAPTCHA:", "method5_marked.png")
        
        iframe_el = page.locator('iframe[src*="recaptcha/api2/bframe"]').first
        box = await iframe_el.bounding_box()
        
        if box:
            test_points = [
                (box['x'] + box['width'] - 45, box['y'] + box['height'] - 100),
                (box['x'] + box['width'] - 50, box['y'] + box['height'] - 90),
                (box['x'] + box['width'] - 40, box['y'] + box['height'] - 110),
            ]
            
            for i, (x, y) in enumerate(test_points):
                await page.evaluate(f"""
                    var d = document.createElement('div');
                    d.style.cssText = 'position:fixed;left:{x-10}px;top:{y-10}px;width:20px;height:20px;background:yellow;border:2px solid red;z-index:999999;border-radius:50%;';
                    document.body.appendChild(d);
                """)
                
                await page.mouse.click(x, y)
                await asyncio.sleep(3)
                
                if await page.locator('.recaptcha-checkbox-checked').is_visible():
                    send_tg(f"✅ نجحت الطريقة 5 عند النقطة {i+1}")
                    return True
        
    except Exception as e:
        send_tg(f"❌ فشلت الطريقة 5: {e}")
    
    await page.screenshot(path="method5_final.png")
    send_tg("📸 نتيجة الطريقة 5:", "method5_final.png")
    return False

async def method_6_extension_popup(page):
    """الطريقة 6: فتح popup الإضافة"""
    send_tg("🎯 الطريقة 6: Extension Popup")
    
    try:
        await page.goto("chrome-extension://pkdpajiblgjahglcmbcggmmgnfmnmcgm/src/options/index.html")
        await asyncio.sleep(2)
        await page.screenshot(path="buster_options.png")
        send_tg("📸 إعدادات Buster:", "buster_options.png")
        
        await page.goto(LAB_URL, timeout=60000)
        await asyncio.sleep(3)
        
        await page.evaluate("""
            () => {
                chrome.runtime.sendMessage('pkdpajiblgjahglcmbcggmmgnfmnmcgm', {action: 'solve'}, (response) => {
                    console.log(response);
                });
            }
        """)
        
        await asyncio.sleep(5)
        
    except Exception as e:
        send_tg(f"❌ فشلت الطريقة 6: {e}")
    
    await page.screenshot(path="method6_popup.png")
    send_tg("📸 نتيجة الطريقة 6:", "method6_popup.png")
    return False

# ===============================================
# 🛡️ طريقة بسيطة لإخفاء Automation (بدون إفساد الصفحة)
# ===============================================

async def simple_stealth(page):
    """إخفاء بسيط لا يؤثر على عمل الصفحة"""
    try:
        # فقط إخفاء webdriver - لا شيء آخر
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        send_tg("🛡️ تم تطبيق إخفاء بسيط")
    except:
        pass

async def try_all_buster_methods(page):
    """تجربة جميع الطرق بالتسلسل"""
    send_tg("🚀 بدء تجربة جميع طرق Buster...")
    
    methods = [
        ("Shadow DOM", method_1_shadow_dom_click),
        ("Keyboard Shortcut", method_2_keyboard_shortcut),
        ("JavaScript Injection", method_3_js_injection),
        ("Dynamic Coordinates", method_4_dynamic_coordinates),
        ("Visual Detection", method_5_visual_detection),
        ("Extension Popup", method_6_extension_popup),
    ]
    
    results = []
    
    for name, method in methods:
        send_tg(f"\n{'='*20}\n🧪 تجربة: {name}\n{'='*20}")
        
        if await page.locator('.recaptcha-checkbox-checked').is_visible():
            send_tg("✅ تم الحل بالفعل!")
            break
        
        if not await page.locator('iframe[src*="recaptcha/api2/bframe"]').is_visible():
            send_tg("🔄 إعادة فتح الكابتشا...")
            await click_captcha_checkbox(page)
            await asyncio.sleep(3)
        
        success = await method(page)
        results.append((name, success))
        
        if success:
            send_tg(f"🏆 النجاح بـ: {name}")
            break
        
        await asyncio.sleep(2)
    
    report = "📊 تقرير النتائج:\n" + "\n".join([f"{'✅' if r else '❌'} {n}" for n, r in results])
    send_tg(report)
    
    await page.screenshot(path="final_result.png")
    send_tg("📸 الصورة النهائية:", "final_result.png")
    
    return any([r for _, r in results])

async def run():
    send_tg("🚀 بدء المهمة...")
    ext_path = await setup_compiled_buster()
    if not ext_path: 
        return

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            "/tmp/chrome_diag",
            headless=False,
            args=[
                f"--disable-extensions-except={ext_path}", 
                f"--load-extension={ext_path}", 
                "--headless=new", 
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process"
            ],
            proxy=WORKING_PROXY,
            viewport={'width': 1280, 'height': 720}
        )
        page = context.pages[0]
        
        try:
            # 🛡️ تطبيق إخفاء بسيط فقط
            await simple_stealth(page)
            
            await context.add_cookies(MY_COOKIES)
            
            # فحص الإضافات
            await page.goto("chrome://extensions/")
            await asyncio.sleep(2)
            await page.screenshot(path="diag_extensions.png")
            send_tg("📸 الإضافات:", "diag_extensions.png")
            
            # الدخول للاب
            await page.goto(LAB_URL, timeout=60000)
            await asyncio.sleep(4)
            await dismiss_credits_modal(page)
            
            await page.screenshot(path="diag_lab_page.png")
            send_tg("🌐 صفحة اللاب:", "diag_lab_page.png")
            
            # بدء اللاب
            if await click_start_lab_button(page):
                await asyncio.sleep(5)
                await page.screenshot(path="diag_after_start.png")
                send_tg("📸 بعد Start Lab:", "diag_after_start.png")
                
                if await click_captcha_checkbox(page):
                    await asyncio.sleep(3)
                    await try_all_buster_methods(page)
                else:
                    send_tg("❌ لم يظهر مربع الكابتشا")

        except Exception as e:
            send_tg(f"🔥 خطأ: {e}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run())
