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

def random_delay(min_sec=1, max_sec=4):
    """تأخير عشوائي بشري"""
    return random.uniform(min_sec, max_sec)

async def human_like_mouse_move(page, target_x, target_y):
    """حركة فأرة بشرية مع انحناءات"""
    try:
        # الحصول على الموقع الحالي
        current = await page.evaluate("""() => {
            return {x: window.lastMouseX || 0, y: window.lastMouseY || 0}
        }""")
        
        steps = random.randint(15, 25)
        for i in range(steps):
            t = i / steps
            # منحنى بيزيه للحركة الطبيعية
            x = current['x'] + (target_x - current['x']) * t + random.randint(-10, 10) * (1-t)
            y = current['y'] + (target_y - current['y']) * t + random.randint(-10, 10) * (1-t)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.03, 0.08))
        
        # تحديث الموقع الأخير
        await page.evaluate(f"window.lastMouseX = {target_x}; window.lastMouseY = {target_y}")
    except:
        pass

async def setup_compiled_buster():
    ext_dir = os.path.abspath("buster_compiled_ext")
    if os.path.exists(ext_dir): 
        shutil.rmtree(ext_dir)
    os.makedirs(ext_dir)
    zip_path = "buster_ready.zip"
    
    try:
        r = requests.get(BUSTER_COMPILED_URL, timeout=30)
        with open(zip_path, "wb") as f: 
            f.write(r.content)
        with zipfile.ZipFile(zip_path, 'r') as z: 
            z.extractall(ext_dir)
        os.remove(zip_path)
        return ext_dir
    except:
        return None

async def dismiss_credits_modal(page):
    try:
        btn = page.get_by_role("button", name=re.compile(r"Dismiss", re.I))
        if await btn.count() > 0 and await btn.first.is_visible():
            await btn.first.click()
            await asyncio.sleep(random_delay())
            return True
    except: 
        pass
    return False

async def click_start_lab_button(page):
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)
    for _ in range(30):
        try:
            btn = page.get_by_role("button", name=pattern).first
            if await btn.is_visible():
                box = await btn.bounding_box()
                await human_like_mouse_move(page, box['x'] + box['width']/2, box['y'] + box['height']/2)
                await asyncio.sleep(random.uniform(0.2, 0.5))
                await page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                return True
        except: 
            pass
        await asyncio.sleep(1)
    return False

async def click_captcha_checkbox(page):
    await asyncio.sleep(random_delay(2, 4))
    iframes = await page.locator('iframe[title*="reCAPTCHA"]').all()
    for iframe in iframes:
        try:
            frame_content = iframe.content_frame
            checkbox = frame_content.locator('.recaptcha-checkbox-border').first
            if await checkbox.is_visible():
                box = await checkbox.bounding_box()
                await human_like_mouse_move(page, box['x'] + box['width']/2, box['y'] + box['height']/2)
                await asyncio.sleep(random.uniform(0.3, 0.7))
                await page.mouse.down()
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await page.mouse.up()
                return True
        except: 
            continue
    return False

# ===============================================
# 🛡️ طرق التخفي من الاكتشاف
# ===============================================

async def apply_stealth_scripts(page):
    """حقن سكربتات إخفاء الـ automation"""
    
    scripts = [
        # إخفاء webdriver
        """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """,
        
        # إخفاء plugins
        """
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        """,
        
        # إخفاء languages
        """
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'ar']
        });
        """,
        
        # إخفاء permissions
        """
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """,
        
        # إخفاء chrome runtime
        """
        window.chrome = {
            runtime: {
                OnInstalledReason: {CHROME_UPDATE: "chrome_update", EXTENSION_UPDATE: "extension_update", INSTALL: "install", SHARED_MODULE_UPDATE: "shared_module_update", UPDATE: "update"},
                OnRestartRequiredReason: {APP_UPDATE: "app_update", OS_UPDATE: "os_update", PERIODIC: "periodic"},
                PlatformArch: {ARM: "arm", ARM64: "arm64", MIPS: "mips", MIPS64: "mips64", X86_32: "x86-32", X86_64: "x86-64"},
                PlatformNaclArch: {MIPS: "mips", MIPS64: "mips64", MIPS64EL: "mips64el", MIPSEL: "mipsel", X86_32: "x86-32", X86_64: "x86-64"},
                PlatformOs: {ANDROID: "android", CROS: "cros", LINUX: "linux", MAC: "mac", OPENBSD: "openbsd", WIN: "win"},
                RequestUpdateCheckStatus: {NO_UPDATE: "no_update", THROTTLED: "throttled", UPDATE_AVAILABLE: "update_available"}
            }
        };
        """,
        
        # إخفاء iframe detection
        """
        const originalAttachShadow = Element.prototype.attachShadow;
        Element.prototype.attachShadow = function(options) {
            const shadow = originalAttachShadow.call(this, options);
            Object.defineProperty(shadow, 'mode', { value: 'open' });
            return shadow;
        };
        """
    ]
    
    for script in scripts:
        try:
            await page.add_init_script(script)
        except:
            pass
    
    send_tg("🛡️ تم تطبيق Stealth Scripts")

async def simulate_human_behavior(page):
    """محاكاة سلوك بشري: تمرير، حركات عشوائية"""
    try:
        # تمرير عشوائي
        for _ in range(random.randint(2, 5)):
            scroll_y = random.randint(100, 500)
            await page.evaluate(f"window.scrollBy(0, {scroll_y})")
            await asyncio.sleep(random.uniform(0.5, 2))
        
        # حركة فأرة عشوائية
        for _ in range(random.randint(3, 7)):
            x, y = random.randint(100, 800), random.randint(100, 600)
            await human_like_mouse_move(page, x, y)
            await asyncio.sleep(random.uniform(0.3, 1.5))
            
    except:
        pass

# ===============================================
# 🔥 طرق Buster المحسّنة
# ===============================================

async def method_1_shadow_dom_v2(page):
    """الطريقة 1: Shadow DOM مع تأخيرات بشرية"""
    send_tg("🎯 الطريقة 1: Shadow DOM v2")
    
    try:
        challenge_iframe = page.frame_locator('iframe[src*="recaptcha/api2/bframe"]').first
        
        # التحويل للصوت بتأخير بشري
        await asyncio.sleep(random_delay(2, 4))
        audio_btn = challenge_iframe.locator('#recaptcha-audio-button')
        if await audio_btn.is_visible():
            box = await audio_btn.bounding_box()
            await human_like_mouse_move(page, box['x'] + 10, box['y'] + 10)
            await asyncio.sleep(random.uniform(0.3, 0.6))
            await page.mouse.click(box['x'] + 10, box['y'] + 10)
            send_tg("🔊 تم التحويل للصوت (بشري)")
            await asyncio.sleep(random_delay(3, 5))
        
        # البحث عن Buster
        buster_selectors = [
            'button[title*="Buster"]',
            'button[class*="buster"]',
            'div[class*="buster"]',
            '[data-buster]',
            'button[aria-label*="solve"]'
        ]
        
        for selector in buster_selectors:
            try:
                btn = challenge_iframe.locator(selector).first
                if await btn.is_visible(timeout=3000):
                    box = await btn.bounding_box()
                    await human_like_mouse_move(page, box['x'] + box['width']/2, box['y'] + box['height']/2)
                    await asyncio.sleep(random.uniform(0.4, 0.8))
                    await page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    
                    await asyncio.sleep(random_delay(8, 12))
                    
                    verify_btn = challenge_iframe.locator('#recaptcha-verify-button')
                    if await verify_btn.is_visible():
                        await verify_btn.click()
                    
                    return True
            except:
                continue
                
    except Exception as e:
        send_tg(f"❌ طريقة 1: {e}")
    
    await page.screenshot(path="method1_v2.png")
    send_tg("📸 طريقة 1:", "method1_v2.png")
    return False

async def method_2_iframe_injection(page):
    """الطريقة 2: حقن JS داخل iframe مباشرة"""
    send_tg("🎯 الطريقة 2: Iframe Injection")
    
    try:
        iframe = page.locator('iframe[src*="recaptcha/api2/bframe"]').first
        frame = iframe.content_frame
        
        # حقن JS للضغط على Buster
        result = await frame.evaluate("""() => {
            // التحويل للصوت
            const audioBtn = document.querySelector('#recaptcha-audio-button');
            if (audioBtn) {
                audioBtn.click();
                return 'audio_clicked';
            }
            return 'no_audio';
        }""")
        
        send_tg(f"🔊 نتيجة الصوت: {result}")
        await asyncio.sleep(random_delay(4, 6))
        
        # البحث والضغط على Buster
        click_result = await frame.evaluate("""() => {
            const buttons = document.querySelectorAll('button, div');
            for (let btn of buttons) {
                if (btn.textContent.toLowerCase().includes('buster') || 
                    btn.className.includes('buster') ||
                    btn.getAttribute('title')?.includes('Buster')) {
                    btn.click();
                    return 'buster_clicked';
                }
            }
            return 'not_found';
        }""")
        
        send_tg(f"🤖 نتيجة Buster: {click_result}")
        await asyncio.sleep(random_delay(8, 12))
        
        if await page.locator('.recaptcha-checkbox-checked').is_visible():
            return True
            
    except Exception as e:
        send_tg(f"❌ طريقة 2: {e}")
    
    await page.screenshot(path="method2_injection.png")
    send_tg("📸 طريقة 2:", "method2_injection.png")
    return False

async def method_3_visual_scan(page):
    """الطريقة 3: مسح بصري للأيقونة"""
    send_tg("🎯 الطريقة 3: Visual Scan")
    
    try:
        iframe_el = page.locator('iframe[src*="recaptcha/api2/bframe"]').first
        box = await iframe_el.bounding_box()
        
        if not box:
            return False
        
        # نقاط محتملة للأيقونة (9 مواقع)
        potential_points = []
        for px in [0.75, 0.80, 0.85, 0.90]:
            for py in [0.65, 0.70, 0.75, 0.80]:
                x = box['x'] + (box['width'] * px)
                y = box['y'] + (box['height'] * py)
                potential_points.append((x, y, px, py))
        
        for i, (x, y, px, py) in enumerate(potential_points):
            # رسم علامة
            await page.evaluate(f"""
                var d = document.createElement('div');
                d.id = 'test-marker-{i}';
                d.style.cssText = 'position:fixed;left:{x-15}px;top:{y-15}px;width:30px;height:30px;background:rgba(255,0,0,0.5);border:2px solid yellow;z-index:999999;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:12px;';
                d.innerHTML = '{i+1}';
                document.body.appendChild(d);
            """)
            
            await human_like_mouse_move(page, x, y)
            await asyncio.sleep(random.uniform(0.5, 1))
            await page.mouse.click(x, y)
            await asyncio.sleep(random_delay(5, 8))
            
            # إزالة العلامة
            await page.evaluate(f"document.getElementById('test-marker-{i}')?.remove()")
            
            if await page.locator('.recaptcha-checkbox-checked').is_visible():
                send_tg(f"✅ نجحت عند النقطة {i+1} ({px:.2f}, {py:.2f})")
                return True
        
    except Exception as e:
        send_tg(f"❌ طريقة 3: {e}")
    
    await page.screenshot(path="method3_visual.png")
    send_tg("📸 طريقة 3:", "method3_visual.png")
    return False

async def method_4_keyboard_human(page):
    """الطريقة 4: اختصارات مع تأخيرات بشرية"""
    send_tg("🎯 الطريقة 4: Human-like Keyboard")
    
    try:
        iframe = page.frame_locator('iframe[src*="recaptcha/api2/bframe"]').first
        await iframe.locator('body').click()
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # كتابة نص عشوائي أولاً (للتمويه)
        fake_text = "checking this website"
        for char in fake_text:
            await page.keyboard.press(f"Key{char.upper()}" if char.isalpha() else char)
            await asyncio.sleep(random.uniform(0.05, 0.15))
        
        await asyncio.sleep(random.uniform(1, 2))
        
        # الاختصار
        shortcuts = ['Control+Shift+KeyS', 'Control+Shift+KeyA', 'Alt+Shift+KeyS']
        for shortcut in shortcuts:
            await page.keyboard.press(shortcut)
            await asyncio.sleep(random_delay(4, 7))
            
            if await page.locator('.recaptcha-checkbox-checked').is_visible():
                send_tg(f"✅ نجح الاختصار: {shortcut}")
                return True
        
    except Exception as e:
        send_tg(f"❌ طريقة 4: {e}")
    
    await page.screenshot(path="method4_keyboard.png")
    send_tg("📸 طريقة 4:", "method4_keyboard.png")
    return False

async def try_all_methods(page):
    """تجربة جميع الطرق بالتسلسل"""
    send_tg("🚀 بدء تجربة جميع الطرق...")
    
    methods = [
        method_1_shadow_dom_v2,
        method_2_iframe_injection,
        method_3_visual_scan,
        method_4_keyboard_human,
    ]
    
    for method in methods:
        if await page.locator('.recaptcha-checkbox-checked').is_visible():
            send_tg("✅ تم الحل!")
            break
        
        # إعادة فتح الكابتشا إذا لزم
        if not await page.locator('iframe[src*="recaptcha/api2/bframe"]').is_visible():
            await click_captcha_checkbox(page)
            await asyncio.sleep(random_delay(3, 5))
        
        success = await method(page)
        if success:
            send_tg(f"🏆 النجاح بـ: {method.__name__}")
            break
        
        await asyncio.sleep(random_delay(2, 4))
    
    await page.screenshot(path="final_result.png")
    send_tg("📸 النتيجة النهائية:", "final_result.png")

async def run():
    send_tg("🚀 بدء المحاولة بـ Stealth Mode...")
    ext_path = await setup_compiled_buster()
    
    async with async_playwright() as p:
        # 🛡️ إعدادات متقدمة للتخفي
        context = await p.chromium.launch_persistent_context(
            "/tmp/chrome_stealth_v2",
            headless=False,
            args=[
                f"--disable-extensions-except={ext_path}", 
                f"--load-extension={ext_path}",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-web-security",
                "--window-size=1366,768",
                "--start-maximized",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                # إخفاء أنه headless
                "--headless=new",
            ],
            proxy=WORKING_PROXY,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.0",
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="America/New_York",
            geolocation={"latitude": 40.7128, "longitude": -74.0060},  # NYC
            permissions=["geolocation"],
            color_scheme="light",
        )
        
        page = context.pages[0]
        
        # 🛡️ تطبيق Stealth Scripts
        await apply_stealth_scripts(page)
        
        try:
            await context.add_cookies(MY_COOKIES)
            
            # 🎭 محاكاة سلوك بشري قبل الدخول
            await simulate_human_behavior(page)
            
            await page.goto(LAB_URL, timeout=60000)
            await asyncio.sleep(random_delay(3, 6))
            
            await dismiss_credits_modal(page)
            await simulate_human_behavior(page)
            
            if await click_start_lab_button(page):
                await asyncio.sleep(random_delay(5, 8))
                
                if await click_captcha_checkbox(page):
                    await asyncio.sleep(random_delay(4, 6))
                    await try_all_methods(page)
                else:
                    send_tg("❌ لم يظهر مربع الكابتشا")

        except Exception as e:
            send_tg(f"🔥 خطأ: {e}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run())
