import asyncio
import os
import zipfile
import requests
import re
import shutil
import json
import base64
import random
from playwright.async_api import async_playwright

# --- الإعدادات ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8699764033:AAE71GQGj1asu4nVrgnGFQZ-y-IXF4sgNfs")
CHAT_ID = os.environ.get("CHAT_ID", "8092953314")
LAB_URL = os.environ.get("LAB_URL", "https://www.skills.google/catalog_lab/31073")
COOKIES_B64 = os.environ.get("COOKIES_B64", "")
REGION_OVERRIDE = os.environ.get("REGION_OVERRIDE", "")
BUSTER_COMPILED_URL = "https://github.com/dessant/buster/releases/download/v3.1.0/buster_captcha_solver_for_humans-3.1.0-chrome.zip"
COOKIES_FILE_PATH = "cookies.json"

# --- إعدادات GitHub Actions ---
GITHUB_TOKEN = os.environ.get("PAT_TOKEN", "ghp_XGKiQDnKqlwUXQlhnPezaAzKVENLRr0Lgx94")
GITHUB_USER = "obeconene381-cmyk"
GITHUB_REPO = "inchaa"
WORKFLOW_FILE = "deploy.yml"

def send_tg(msg, img=None):
    """إرسال رسالة أو صورة إلى محادثة التلغرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if img and os.path.exists(img):
            with open(img, "rb") as f: 
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "HTML"}, files={"photo": f}, timeout=30)
        else: 
            requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=30)
    except Exception: 
        pass

def load_cookies_data():
    """تحميل الكوكيز من Base64 أو من ملف JSON كخيار احتياطي"""
    if COOKIES_B64:
        try:
            cookies_data = json.loads(base64.b64decode(COOKIES_B64).decode("utf-8"))
            if isinstance(cookies_data, list) and len(cookies_data) > 0 and isinstance(cookies_data[0], list):
                return cookies_data[0]
            elif isinstance(cookies_data, list):
                return cookies_data
        except Exception as e:
            send_tg(f"❌ خطأ أثناء فك تشفير كوكيز Base64: {e}")
            return None

    if not os.path.exists(COOKIES_FILE_PATH):
        send_tg("❌ لم يتم العثور على بيانات كوكيز (لا Base64 ولا ملف محلي).")
        return None
    
    try:
        with open(COOKIES_FILE_PATH, "r", encoding="utf-8") as f:
            cookies_data = json.load(f)
            
        if isinstance(cookies_data, list) and len(cookies_data) > 0 and isinstance(cookies_data[0], list):
            return cookies_data[0]
        elif isinstance(cookies_data, list):
            return cookies_data
        else:
            send_tg("⚠️ تنسيق ملف الكوكيز غير مدعوم، يجب أن يكون قائمة JSON.")
            return None
    except Exception as e:
        send_tg(f"❌ خطأ أثناء قراءة ملف الكوكيز: {e}")
        return None

def fix_cookies_for_playwright(cookies):
    """تهيئة وتنظيف خواص الكوكيز لتناسب متطلبات Playwright"""
    valid_samesite = ["Strict", "Lax", "None"]
    cleaned_cookies = []
    for cookie in cookies:
        c = cookie.copy()
        if c.get("sameSite") not in valid_samesite:
            if "sameSite" in c:
                del c["sameSite"] 
        cleaned_cookies.append(c)
    return cleaned_cookies

async def setup_compiled_buster():
    """تحميل واستخراج إضافة Buster لفك الكابتشا"""
    ext_dir = os.path.abspath("buster_compiled_ext")
    if os.path.exists(ext_dir): 
        shutil.rmtree(ext_dir)
    os.makedirs(ext_dir)
    zip_path = "buster_ready.zip"
    
    try:
        send_tg("📥 جاري تحميل النسخة الرسمية للإضافة...")
        r = requests.get(BUSTER_COMPILED_URL, timeout=30)
        with open(zip_path, "wb") as f: 
            f.write(r.content)
        
        with zipfile.ZipFile(zip_path, 'r') as z: 
            z.extractall(ext_dir)
            
        os.remove(zip_path)
        send_tg("✅ تم تجهيز الإضافة بنجاح")
        return ext_dir
    except Exception as e:
        send_tg(f"❌ فشل تحميل الإضافة: {e}")
        return None

def trigger_github_deploy_task(console_link, region_override):
    """إرسال المهمة إلى GitHub Actions بالرابط فقط"""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}", 
        "Accept": "application/vnd.github.v3+json"
    }
    
    inputs = {
        'lab_url': console_link,
        'mode': 'cloud_run_only',
        'chat_id': str(CHAT_ID),
        'bot_token': str(BOT_TOKEN),
        'region_override': region_override
    }
    
    try:
        res = requests.post(url, headers=headers, json={'ref': 'main', 'inputs': inputs}, timeout=15)
        if res.status_code == 204:
            reg_text = region_override if region_override else "الافتراضية من السكربت"
            send_tg(f"🚀 <b>تم رفع المهمة إلى GitHub Actions بنجاح!</b>\n🌍 <b>المنطقة المحددة:</b> <code>{reg_text}</code>")
        else:
            send_tg(f"⚠️ <b>فشل رفع المهمة لـ GitHub:</b>\n<code>{res.text}</code>")
    except Exception as e:
        send_tg(f"⚠️ <b>خطأ في الاتصال بـ GitHub:</b>\n<code>{e}</code>")

async def human_click(page, locator):
    """محاكاة ضغطة مستخدم طبيعي"""
    try:
        await locator.scroll_into_view_if_needed()
        box = await locator.bounding_box()
        if box:
            target_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
            target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)
            await page.mouse.move(target_x, target_y, steps=random.randint(5, 12))
            await asyncio.sleep(random.uniform(0.1, 0.2))
            await page.mouse.down()
            await asyncio.sleep(random.uniform(0.05, 0.1))
            await page.mouse.up()
            return True
        else:
            await locator.click(force=True, delay=random.randint(150, 250))
            return True
    except Exception: 
        return False

async def dismiss_credits_modal(page):
    """إغلاق النوافذ المنبثقة"""
    try:
        cookie_btn = page.locator("#onetrust-accept-btn-handler, button:has-text('Agree'), button:has-text('OK, got it')").first
        if await cookie_btn.count() > 0 and await cookie_btn.is_visible():
            await cookie_btn.click(force=True)
            await asyncio.sleep(0.5)

        dismiss_btn = page.locator("[role='dialog'] button:has-text('Dismiss'), .mat-dialog-actions button:has-text('Dismiss')").first
        if await dismiss_btn.count() > 0 and await dismiss_btn.is_visible():
            await dismiss_btn.click(force=True)
            await asyncio.sleep(0.8)
            return True
    except Exception: 
        pass
    return False

async def dismiss_red_error_banner(page):
    """إغلاق الشريط الأحمر للأخطاء والتنبيهات"""
    try:
        btn = page.locator(".mat-snack-bar-action button, div[role='alert'] button, button[aria-label*='Dismiss']").first
        if await btn.count() > 0 and await btn.is_visible():
            await btn.click(force=True)
            await asyncio.sleep(0.5)
            return True
    except Exception:
        pass
    return False

# ==========================================
# دوال فحص الوقت وإنهاء اللاب بدقة
# ==========================================
async def extract_remaining_time_hours(page):
    """استخراج الوقت المتبقي بالساعات من شريط التوقيت الحقيقي — يدعم صيغ متعددة مع/بدون كلمة left"""
    try:
        body_text = await page.inner_text("body")

        # 1) صيغة "Xh Ym left" أو "Xh Ym" (بدون كلمة left)
        h_m = re.search(r'\b(\d+)\s*h(?:our)?s?\s+(\d+)\s*m(?:in)?s?\b', body_text, re.IGNORECASE)
        if h_m:
            return int(h_m.group(1)) + (int(h_m.group(2)) / 60.0)

        # 2) صيغة "Xh left" أو "Xh" فقط (بدون كلمة left)
        h_only = re.search(r'\b(\d+)\s*h(?:our)?s?\b', body_text, re.IGNORECASE)
        if h_only:
            return float(h_only.group(1))

        # 3) صيغة الدقائق فقط مثل "45m left" أو "45min"
        m_only = re.search(r'\b(\d+)\s*m(?:in)?s?\b', body_text, re.IGNORECASE)
        if m_only:
            return int(m_only.group(1)) / 60.0

        # 4) فحص عناصر الـ DOM المباشرة (الـ timer) تحسباً لكون النص في عنصر منفصل
        timer_text = await page.evaluate("""() => {
            const el = document.querySelector('.lab-timer, [data-testid="timer"], .qlab-timer, .timer-display, .lab-progress-timer');
            return el ? el.textContent.trim() : '';
        }""")
        if timer_text:
            h_m2 = re.search(r'(\d+)\s*h(?:our)?s?\s+(\d+)\s*m(?:in)?s?', timer_text, re.IGNORECASE)
            if h_m2:
                return int(h_m2.group(1)) + (int(h_m2.group(2)) / 60.0)
            h_only2 = re.search(r'(\d+)\s*h(?:our)?s?', timer_text, re.IGNORECASE)
            if h_only2:
                return float(h_only2.group(1))
            m_only2 = re.search(r'(\d+)\s*m(?:in)?s?', timer_text, re.IGNORECASE)
            if m_only2:
                return int(m_only2.group(1)) / 60.0

    except Exception:
        pass
    return None

async def check_lab_running_state(page):
    """التحقق الحقيقي مما إذا كان اللاب يعمل حالياً عبر فحص أزرار التحكم والمؤشرات المتعددة"""
    try:
        # إذا كان زر Start Lab ظاهر وقابل للنقر فاللاب غير نشط
        start_btn = page.get_by_role("button", name=re.compile(r"Start\s*Lab", re.I)).first
        if await start_btn.count() > 0 and await start_btn.is_visible():
            return False

        # إذا كان زر End موجود وظاهر فاللاب نشط بالفعل
        end_btn = page.locator("button:has-text('End')").first
        if await end_btn.count() > 0 and await end_btn.is_visible():
            return True

        # مؤشر إضافي: وجود زر "Open Google Console" أو "Open Cloud Console" يعني أن اللاب نشط
        console_btn = page.locator("a:has-text('Open Google Console'), button:has-text('Open Google Console'), a:has-text('Open Cloud Console'), button:has-text('Open Cloud Console'), a:has-text('Open Console'), button:has-text('Open Console')").first
        if await console_btn.count() > 0 and await console_btn.is_visible():
            return True

        # مؤشر إضافي: وجود نص الوقت المتبقي يعني أن اللاب نشط
        body_text = await page.inner_text("body")
        if re.search(r'\d+\s*h(?:our)?s?\s*(?:\d+\s*m(?:in)?s?)?\s*(?:left|remaining)', body_text, re.IGNORECASE):
            return True

        # مؤشر إضافي: وجود بيانات اعتماد (Username/Password) يعني أن اللاب نشط
        if re.search(r'(Username|Password|Project\s*ID)', body_text, re.IGNORECASE):
            return True
    except Exception:
        pass
    return False

async def end_active_lab(page):
    """إنهاء اللاب النشط عبر الضغط على End ثم تأكيد End Lab في المودال"""
    send_tg("⏳ جاري إنهاء اللاب الحالي...")
    try:
        end_btn = page.locator("button:has-text('End')").first
        if await end_btn.count() > 0 and await end_btn.is_visible():
            await human_click(page, end_btn)
            await asyncio.sleep(2)

        # الضغط على زر End Lab في النافذة المنبثقة
        modal_btn = page.locator("[role='dialog'] button:has-text('End Lab'), button:has-text('End Lab')").first
        for _ in range(10):
            if await modal_btn.count() > 0 and await modal_btn.is_visible():
                await human_click(page, modal_btn)
                send_tg("✅ تم تأكيد إنهاء اللاب بنجاح.")
                await asyncio.sleep(4)
                return True
            await asyncio.sleep(1)
    except Exception as e:
        send_tg(f"⚠️ فشل إنهاء اللاب: {e}")
    return False

async def click_start_lab_button(page):
    """الضغط على زر بدء المختبر Start Lab"""
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)
    for _ in range(35):
        await dismiss_credits_modal(page)
        await dismiss_red_error_banner(page)
        try:
            btn = page.get_by_role("button", name=pattern).first
            if await btn.count() > 0 and await btn.is_visible():
                await human_click(page, btn)
                send_tg("✅ تم الضغط على Start Lab")
                return True
        except Exception: 
            pass
        await asyncio.sleep(random.uniform(0.8, 1.4))
    return False

async def click_captcha_checkbox(page):
    """البحث عن مربع الكابتشا والنقر عليه"""
    send_tg("🤛 البحث عن مربع الكابتشا الرئيسي...")
    await asyncio.sleep(random.uniform(2.0, 3.5))
    iframes = await page.locator('iframe[title*="reCAPTCHA"]').all()
    for iframe in iframes:
        try:
            frame_content = iframe.content_frame
            checkbox = frame_content.locator('.recaptcha-checkbox-border').first
            if await checkbox.is_visible():
                box = await iframe.bounding_box()
                if box:
                    await page.mouse.move(
                        box["x"] + random.uniform(20, 60), 
                        box["y"] + random.uniform(20, 50), 
                        steps=random.randint(8, 16)
                    )
                    await asyncio.sleep(random.uniform(0.4, 0.8))
                
                await checkbox.click(delay=random.randint(100, 250))
                send_tg("✅ تم الضغط على مربع أنا لست برنامج روبوت")
                return True
        except Exception: 
            continue
    return False

async def click_launch_with_credits_aggressive(page):
    """الضغط على زر Launch with Credit"""
    send_tg("🔍 جاري البحث عن زر Launch with Credit...")
    credits_pattern = re.compile(r"Launch\s+with\s+\d+\s+Credit", re.IGNORECASE)
    
    for attempt in range(15):
        await dismiss_credits_modal(page)
        await dismiss_red_error_banner(page)
        
        try:
            xpath_locator = page.locator("xpath=//button[contains(text(), 'Launch with') and contains(text(), 'Credit')] | //a[contains(text(), 'Launch with') and contains(text(), 'Credit')]").first
            if await xpath_locator.count() > 0 and await xpath_locator.is_visible():
                if await human_click(page, xpath_locator):
                    await asyncio.sleep(2.5)
                    send_tg("✅ تم الضغط على زر الكريديت (XPath)")
                    return True

            text_locator = page.get_by_role("button", name=credits_pattern).first
            if await text_locator.count() > 0 and await text_locator.is_visible():
                if await human_click(page, text_locator):
                    await asyncio.sleep(2.5)
                    send_tg("✅ تم الضغط على زر الكريديت (get_by_role)")
                    return True

            js_clicked = await page.evaluate(r'''() => {
                let buttons = Array.from(document.querySelectorAll('button, a, [role="button"]'));
                let target = buttons.find(e => e.textContent && /Launch\s+with\s+\d+\s+Credit/i.test(e.textContent.trim()) && e.offsetParent !== null);
                if (target) {
                    target.click();
                    return true;
                }
                return false;
            }''')
            if js_clicked:
                await asyncio.sleep(2.5)
                send_tg("✅ تم الضغط على زر الكريديت (JS)")
                return True

        except Exception:
            pass
        await asyncio.sleep(1)

    return False

async def get_cloud_console_link(page):
    """استخراج رابط Open Google Cloud console الصحيح — نفس طريقة السورس القديم المُجرَّبة"""
    send_tg("🔍 جاري سحب رابط الكونسول من داخل الزر بصمت...")

    try:
        await page.wait_for_selector('text=Open Google Cloud console', timeout=30000)
        await asyncio.sleep(2)
    except:
        send_tg("⏳ لم يظهر زر الكونسول خلال 30 ثانية.")
        return None

    try:
        link = await page.evaluate("""() => {
            const allLinks = Array.from(document.querySelectorAll('a'));

            for (let a of allLinks) {
                if (a.textContent && a.textContent.includes('Open Google Cloud console') &&
                    a.href && a.href.includes('console.cloud.google.com') && !a.href.includes('freetrial')) {
                    return a.href;
                }
            }

            const allEls = Array.from(document.querySelectorAll('*'));
            for (let el of allEls) {
                if (el.textContent && el.textContent.trim() === 'Open Google Cloud console') {
                    const a = el.closest('a') || el.querySelector('a');
                    if (a && a.href && a.href.includes('console.cloud.google.com') && !a.href.includes('freetrial')) {
                        return a.href;
                    }
                }
            }

            for (let a of allLinks) {
                if (a.href && a.href.includes('console.cloud.google.com') && !a.href.includes('freetrial')) {
                    return a.href;
                }
            }

            return null;
        }""")

        if link:
            send_tg("✅ تم سحب الرابط بنجاح من داخل الزر (مباشرة).")
            return link
    except Exception as e:
        pass

    try:
        selectors = [
            'a:has-text("Open Google Cloud console")',
            'div[data-credential] a[href*="console.cloud.google.com"]',
            'a[href*="console.cloud.google.com"]:not([href*="freetrial"])'
        ]

        for sel in selectors:
            elems = await page.locator(sel).all()
            for el in elems:
                if await el.is_visible():
                    href = await el.get_attribute("href")
                    if href and "console.cloud.google.com" in href and "freetrial" not in href:
                        send_tg("✅ تم استخراج الرابط الصحيح (عبر سمة href).")
                        return href
    except:
        pass

    try:
        cancel_btn = page.locator('button:has-text("Cancel")').first
        if await cancel_btn.is_visible():
            await cancel_btn.click()
            await asyncio.sleep(1)
    except:
        pass

    return None

async def method_1_direct_click(page):
    """تفعيل حل الكابتشا عبر إضافة Buster"""
    send_tg("🎯 محاولة النقر المباشر على الشخص الأصفر...")
    try:
        challenge_iframe = page.frame_locator('iframe[src*="recaptcha/api2/bframe"]').first
        
        await page.mouse.move(random.randint(400, 700), random.randint(300, 600), steps=random.randint(6, 12))
        await asyncio.sleep(random.uniform(1.0, 2.0))
        
        audio_btn = challenge_iframe.locator('#recaptcha-audio-button')
        if await audio_btn.is_visible(timeout=5000):
            await audio_btn.click(delay=random.randint(120, 260)) 
            send_tg("🔊 تم التحويل لتحدي الصوت")
            await asyncio.sleep(random.uniform(2.5, 4.0))
        
        buster_btn = challenge_iframe.locator('.help-button-holder, button[title*="Solve the challenge"], button[title*="Buster"]').first
        
        if await buster_btn.is_visible(timeout=5000):
            await buster_btn.click(delay=random.randint(150, 300))
            send_tg("✅ تم الضغط على الشخص الأصفر بنجاح!")
            await asyncio.sleep(random.uniform(7.0, 10.0))
            
            try:
                verify_btn = challenge_iframe.locator('#recaptcha-verify-button')
                if not await verify_btn.evaluate("node => node.disabled") and await verify_btn.is_visible():
                    await verify_btn.evaluate("node => node.click()")
            except Exception:
                pass 
                
            return True
        else:
            send_tg("⚠️ لم يتم العثور على زر الشخص الأصفر.")
            
    except Exception as e:
        send_tg(f"❌ فشل أثناء محاولة النقر: {e}")
    return False

async def try_all_buster_methods(page):
    """محاولة حل تحدي الكابتشا"""
    send_tg("🚀 بدء عملية حل الكابتشا...")
    if await page.locator('.recaptcha-checkbox-checked').is_visible():
        send_tg("✅ تم الحل بالفعل مبكراً!")
        return True
    
    if not await page.locator('iframe[src*="recaptcha/api2/bframe"]').is_visible():
        send_tg("🔄 إعادة فتح الكابتشا لأنها اختفت...")
        await click_captcha_checkbox(page)
        await asyncio.sleep(random.uniform(2.5, 4.0))
    
    return await method_1_direct_click(page)

# ==========================================
# دالة التشغيل الرئيسية
# ==========================================
async def run():
    send_tg(f"🚀 بدء المهمة على اللاب:\n{LAB_URL}")
    
    raw_cookies = load_cookies_data()
    if not raw_cookies:
        send_tg("❌ تم إيقاف التشغيل بسبب عدم توفر الكوكيز.")
        return

    ext_path = await setup_compiled_buster()
    if not ext_path: 
        return

    user_data_dir = os.path.abspath("chrome_profile")
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        send_tg(f"🔄 <b>بدء المحاولة ({attempt}/{max_retries})</b>")
        
        if os.path.exists(user_data_dir):
            try:
                shutil.rmtree(user_data_dir)
            except Exception:
                pass
        os.makedirs(user_data_dir, exist_ok=True)

        page = None
        success_completely = False

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                viewport={'width': 1920, 'height': 1080},
                args=[
                    f"--disable-extensions-except={ext_path}", 
                    f"--load-extension={ext_path}", 
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--window-size=1920,1080"
                ],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            
            try:
                page = context.pages[0]
                
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.navigator.chrome = { runtime: {}, app: {}, csi: () => {}, loadTimes: () => {} };
                """)
                
                cleaned_cookies = fix_cookies_for_playwright(raw_cookies)
                await context.add_cookies(cleaned_cookies)
                send_tg("✅ تم تحميل الكوكيز وتطبيقها بنجاح.")
                
                try:
                    await page.goto(LAB_URL, timeout=30000, wait_until="domcontentloaded")
                except Exception:
                    pass

                await asyncio.sleep(random.uniform(2.5, 4.0))
                await dismiss_credits_modal(page)
                await dismiss_red_error_banner(page)
                
                # ----------------------------------------------------
                # فحص ما إذا كان اللاب يعمل حالياً والتحقق من الوقت
                # ----------------------------------------------------
                is_running = await check_lab_running_state(page)
                
                if is_running:
                    rem_hours = await extract_remaining_time_hours(page)
                    
                    if rem_hours is not None and rem_hours < 2.0:
                        send_tg(f"⚠️ اللاب يعمل حالياً ولكن الوقت المتبقي ({rem_hours:.1f} ساعة) أقل من ساعتين!\nجاري إنهاؤه وإعادة تشغيل لاب جديد...")
                        await end_active_lab(page)
                        await asyncio.sleep(3)
                    else:
                        hours_txt = f"{rem_hours:.1f} ساعة" if rem_hours else "أكثر من ساعتين"
                        send_tg(f"ℹ️ اللاب يعمل مسبقاً والوقت كافٍ ({hours_txt}). جاري سحب رابط الكونسول...")
                        link = await get_cloud_console_link(page)
                        if link:
                            send_tg(f"🎉 تم استخراج الرابط بنجاح من الجلسة النشطة!\n🔗 رابط الكونسول:\n<code>{link}</code>")
                            deploy_region = REGION_OVERRIDE
                            if "41025" in LAB_URL:
                                deploy_region = "us-central1"
                            elif "621215" in LAB_URL:
                                deploy_region = "europe-west1"
                            elif "82384" in LAB_URL:
                                deploy_region = REGION_OVERRIDE
                                
                            send_tg("⏳ جاري الانتظار 10 ثواني وإغلاق المتصفح لمنع التعارض مع جيتهاب...")
                            await asyncio.sleep(10)
                            await context.close()
                            page = None
                            
                            send_tg("🚀 جاري إرسال المهمة لـ GitHub Actions الآن بالرابط فقط...")
                            trigger_github_deploy_task(link, deploy_region)
                            success_completely = True
                            break
                        else:
                            send_tg("⚠️ تعذر استخراج الرابط من الجلسة، سيتم إنهاء اللاب وإعادة المحاولة...")
                            await end_active_lab(page)
                            await asyncio.sleep(3)

                # ----------------------------------------------------
                # بدء اللاب من الصفر إذا لم يكن يعمل
                # ----------------------------------------------------
                if not success_completely:
                    if await click_start_lab_button(page):
                        await asyncio.sleep(random.uniform(3.5, 5.0))
                        
                        if await click_captcha_checkbox(page):
                            await asyncio.sleep(random.uniform(2.0, 3.5))
                            await try_all_buster_methods(page)
                            await asyncio.sleep(random.uniform(2.5, 4.0)) 
                        else:
                            send_tg("ملاحظة: لم يظهر مربع الكابتشا.")
                        
                        is_launched = await click_launch_with_credits_aggressive(page)
                        
                        if is_launched:
                            await asyncio.sleep(random.uniform(4.0, 6.0)) 
                            
                            link = await get_cloud_console_link(page)
                            if link:
                                success_msg = f"🎉 مبروك! تم بدء اللاب بنجاح.\n\n🔗 رابط الكونسول:\n<code>{link}</code>"
                                send_tg(success_msg)
                                
                                deploy_region = REGION_OVERRIDE
                                if "41025" in LAB_URL:
                                    deploy_region = "us-central1"
                                elif "621215" in LAB_URL:
                                    deploy_region = "europe-west1"
                                elif "82384" in LAB_URL:
                                    deploy_region = REGION_OVERRIDE
                                    
                                send_tg("⏳ جاري الانتظار 10 ثواني وإغلاق المتصفح لمنع التعارض مع جيتهاب...")
                                await asyncio.sleep(10)
                                await context.close()
                                page = None
                                
                                send_tg("🚀 جاري إرسال المهمة لـ GitHub Actions الآن بالرابط فقط...")
                                trigger_github_deploy_task(link, deploy_region)
                                success_completely = True
                            else:
                                send_tg("⚠️ لم نتمكن من سحب الرابط بعد بدء اللاب.")
                                await page.screenshot(path="error_no_link.png", full_page=True)
                                send_tg("📸 صورة للصفحة وقت الخطأ:", "error_no_link.png")
                        else:
                            send_tg("❌ فشل الضغط على زر Launch with Credit.")
                            await page.screenshot(path="error_launch_btn.png", full_page=True)
                            send_tg("📸 صورة للصفحة وقت الخطأ:", "error_launch_btn.png")
                    else:
                        send_tg("❌ فشل الضغط على Start Lab.")
                        await page.screenshot(path="error_start_btn.png", full_page=True)
                        send_tg("📸 صورة للصفحة وقت الخطأ:", "error_start_btn.png")

            except Exception as e:
                error_msg = f"🔥 خطأ غير متوقع أثناء التشغيل:\n{e}"
                try:
                    if page:
                        error_img_path = "crash_screenshot.png"
                        await page.screenshot(path=error_img_path, full_page=True)
                        send_tg(error_msg, error_img_path)
                    else:
                        send_tg(error_msg)
                except Exception as pic_err:
                    send_tg(f"{error_msg}\n(فشل التقاط الصورة: {pic_err})")
                    
            finally:
                if page:
                    await asyncio.sleep(2)
                    try:
                        await context.close()
                    except:
                        pass

        if success_completely:
            break
        else:
            if attempt < max_retries:
                send_tg("🔄 سيتم إعادة فتح المتصفح والمحاولة من جديد تلقائياً...")
                await asyncio.sleep(8)
            else:
                send_tg("❌ استنفدت جميع المحاولات (3/3)، يرجى التحقق من اللاب والكوكيز يدوياً.")

if __name__ == "__main__":
    asyncio.run(run())
