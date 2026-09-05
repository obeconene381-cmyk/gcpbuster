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

# --- استلام المتغيرات بأمان من البيئة ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")
ADMIN_ID = os.environ.get("ADMIN_ID", "")
LAB_URL = os.environ.get("LAB_URL", "")
COOKIES_B64 = os.environ.get("COOKIES_B64", "")
REGION_OVERRIDE = os.environ.get("REGION_OVERRIDE", "")

# توكن جيتهاب الخاص برفع المهمة يُسحب من Secret
GITHUB_TOKEN = os.environ.get("PAT_TOKEN", "")
GITHUB_USER = os.environ.get("GITHUB_USER", "obeconene381-cmyk")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "inchaa")
WORKFLOW_FILE = "deploy.yml"

BUSTER_COMPILED_URL = "https://github.com/dessant/buster/releases/download/v3.1.0/buster_captcha_solver_for_humans-3.1.0-chrome.zip"
COOKIES_FILE_PATH = "cookies.json"

def send_user(msg):
    """إرسال رسائل نصية عامة ومختصرة للمستخدم"""
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
    except Exception:
        pass

def send_admin(msg, img_path=None):
    """إرسال صور الفشل والتقارير التفصيلية للآدمن فقط"""
    target = ADMIN_ID if ADMIN_ID else CHAT_ID
    if not BOT_TOKEN or not target:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if img_path and os.path.exists(img_path):
            with open(img_path, "rb") as f:
                requests.post(url + "sendPhoto", data={"chat_id": target, "caption": msg, "parse_mode": "HTML"}, files={"photo": f}, timeout=30)
            try:
                os.remove(img_path)
            except Exception:
                pass
        else:
            requests.post(url + "sendMessage", json={"chat_id": target, "text": msg, "parse_mode": "HTML"}, timeout=15)
    except Exception:
        pass

def load_cookies_data():
    if COOKIES_B64:
        try:
            cookies_data = json.loads(base64.b64decode(COOKIES_B64).decode("utf-8"))
            if isinstance(cookies_data, list) and len(cookies_data) > 0 and isinstance(cookies_data[0], list):
                return cookies_data[0]
            elif isinstance(cookies_data, list):
                return cookies_data
        except Exception:
            send_user("❌ <b>الكوكيز منتهية الصلاحية أو بتنسيق غير صالح.</b>")
            return None

    if os.path.exists(COOKIES_FILE_PATH):
        try:
            with open(COOKIES_FILE_PATH, "r", encoding="utf-8") as f:
                cookies_data = json.load(f)
            if isinstance(cookies_data, list) and len(cookies_data) > 0 and isinstance(cookies_data[0], list):
                return cookies_data[0]
            elif isinstance(cookies_data, list):
                return cookies_data
        except Exception:
            pass

    send_user("❌ <b>الكوكيز منتهية الصلاحية أو غير متوفرة.</b>")
    return None

def fix_cookies_for_playwright(cookies):
    valid_samesite = ["Strict", "Lax", "None"]
    cleaned_cookies = []
    for cookie in cookies:
        c = cookie.copy()
        if c.get("sameSite") not in valid_samesite and "sameSite" in c:
            del c["sameSite"]
        cleaned_cookies.append(c)
    return cleaned_cookies

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
    except Exception as e:
        send_admin(f"⚠️ فشل تجهيز إضافة Buster: {e}")
        return None

def trigger_github_deploy_task(console_link, region_override):
    """إطلاق workflow النشر التلقائي عبر GitHub Token السري"""
    if not GITHUB_TOKEN:
        send_admin("⚠️ لم يتم العثور على PAT_TOKEN في Secrets المستودع!")
        return
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
        if res.status_code != 204:
            send_admin(f"⚠️ خطأ أثناء إطلاق deploy.yml: {res.text}")
    except Exception as e:
        send_admin(f"⚠️ فشل الاتصال لرفع مهمة النشر: {e}")

async def human_click(page, locator):
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

# ==========================================
# دالة إغلاق النوافذ المنبثقة المحسّنة بدقة
# ==========================================
async def dismiss_popups(page):
    """إغلاق النوافذ المنبثقة، بانرات الأخطاء، ونوافذ التنبيه عبر البحث المباشر عن Dismiss"""
    try:
        # 1. فحص وضغط مباشر عبر JavaScript لتخطي أي عوائق في الواجهة
        dismissed_js = await page.evaluate("""() => {
            let clicked = false;
            
            // محاولة الضغط على زر ملفات الكوكيز إذا وُجد
            const cookieBtn = document.querySelector('#onetrust-accept-btn-handler, button#onetrust-accept-btn-handler');
            if (cookieBtn && (cookieBtn.offsetParent !== null || cookieBtn.offsetWidth > 0)) {
                cookieBtn.click();
                clicked = true;
            }

            // فحص كافة الأزرار داخل النوافذ ومربعات الحوار
            const buttons = Array.from(document.querySelectorAll(
                'button, [role="button"], a.mat-button, mat-dialog-container button, ' +
                '.modal button, .ql-dialog button, div[role="dialog"] button, [mat-dialog-close]'
            ));
            
            for (let b of buttons) {
                const text = (b.innerText || b.textContent || '').trim().toLowerCase();
                const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                if (text === 'dismiss' || text.includes('dismiss') || 
                    aria === 'dismiss' || aria.includes('dismiss') ||
                    aria === 'close' || aria.includes('close dialog') ||
                    text === 'got it' || text === 'ok, got it' || text === 'agree') {
                    if (b.offsetParent !== null || b.offsetWidth > 0 || b.offsetHeight > 0) {
                        b.click();
                        clicked = true;
                    }
                }
            }
            return clicked;
        }""")
        if dismissed_js:
            await asyncio.sleep(0.5)

        # 2. محددات احتياطية عبر Playwright تشمل كافة الإطارات
        selectors = [
            "#onetrust-accept-btn-handler",
            "[role='dialog'] button:has-text('Dismiss')",
            "mat-dialog-container button:has-text('Dismiss')",
            ".mat-dialog-actions button:has-text('Dismiss')",
            ".ql-dialog button:has-text('Dismiss')",
            "button[aria-label*='Dismiss']",
            "button[aria-label*='dismiss']",
            "button[aria-label*='Close']",
            "button[aria-label*='close']",
            ".mat-snack-bar-action button",
            "div[role='alert'] button",
            "xpath=//button[contains(translate(text(), 'DISMISS', 'dismiss'), 'dismiss')]"
        ]
        for target in [page] + list(page.frames):
            for sel in selectors:
                try:
                    btn = target.locator(sel).first
                    if await btn.count() > 0 and await btn.is_visible():
                        await btn.click(force=True)
                        await asyncio.sleep(0.5)
                        break
                except Exception:
                    pass
    except Exception:
        pass

async def extract_remaining_time_hours(page):
    try:
        body_text = await page.inner_text("body")
        h_m = re.search(r'\b(\d+)\s*h(?:our)?s?\s+(\d+)\s*m(?:in)?s?\b', body_text, re.IGNORECASE)
        if h_m: return int(h_m.group(1)) + (int(h_m.group(2)) / 60.0)
        h_only = re.search(r'\b(\d+)\s*h(?:our)?s?\b', body_text, re.IGNORECASE)
        if h_only: return float(h_only.group(1))
        m_only = re.search(r'\b(\d+)\s*m(?:in)?s?\b', body_text, re.IGNORECASE)
        if m_only: return int(m_only.group(1)) / 60.0

        timer_text = await page.evaluate("""() => {
            const el = document.querySelector('.lab-timer, [data-testid="timer"], .qlab-timer, .timer-display, .lab-progress-timer');
            return el ? el.textContent.trim() : '';
        }""")
        if timer_text:
            h_m2 = re.search(r'(\d+)\s*h(?:our)?s?\s+(\d+)\s*m(?:in)?s?', timer_text, re.IGNORECASE)
            if h_m2: return int(h_m2.group(1)) + (int(h_m2.group(2)) / 60.0)
            h_only2 = re.search(r'(\d+)\s*h(?:our)?s?', timer_text, re.IGNORECASE)
            if h_only2: return float(h_only2.group(1))
            m_only2 = re.search(r'(\d+)\s*m(?:in)?s?', timer_text, re.IGNORECASE)
            if m_only2: return int(m_only2.group(1)) / 60.0
    except Exception:
        pass
    return None

async def check_lab_running_state(page):
    try:
        start_btn = page.get_by_role("button", name=re.compile(r"Start\s*Lab", re.I)).first
        if await start_btn.count() > 0 and await start_btn.is_visible():
            return False
        end_btn = page.locator("button:has-text('End')").first
        if await end_btn.count() > 0 and await end_btn.is_visible():
            return True
        console_btn = page.locator("a:has-text('Open Google Console'), button:has-text('Open Google Console'), a:has-text('Open Cloud Console'), button:has-text('Open Cloud Console'), a:has-text('Open Console'), button:has-text('Open Console')").first
        if await console_btn.count() > 0 and await console_btn.is_visible():
            return True
        body_text = await page.inner_text("body")
        if re.search(r'(Username|Password|Project\s*ID)', body_text, re.IGNORECASE):
            return True
    except Exception:
        pass
    return False

async def end_active_lab(page):
    try:
        end_btn = page.locator("button:has-text('End')").first
        if await end_btn.count() > 0 and await end_btn.is_visible():
            await human_click(page, end_btn)
            await asyncio.sleep(2)
        modal_btn = page.locator("[role='dialog'] button:has-text('End Lab'), button:has-text('End Lab')").first
        for _ in range(10):
            if await modal_btn.count() > 0 and await modal_btn.is_visible():
                await human_click(page, modal_btn)
                await asyncio.sleep(4)
                return True
            await asyncio.sleep(1)
    except Exception:
        pass
    return False

async def click_start_lab_button(page):
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)
    for _ in range(35):
        await dismiss_popups(page)
        try:
            btn = page.get_by_role("button", name=pattern).first
            if await btn.count() > 0 and await btn.is_visible():
                await human_click(page, btn)
                return True
        except Exception:
            pass
        await asyncio.sleep(random.uniform(0.8, 1.4))
    return False

async def click_captcha_checkbox(page):
    await asyncio.sleep(random.uniform(2.0, 3.5))
    iframes = await page.locator('iframe[title*="reCAPTCHA"]').all()
    for iframe in iframes:
        try:
            checkbox = iframe.content_frame.locator('.recaptcha-checkbox-border').first
            if await checkbox.is_visible():
                box = await iframe.bounding_box()
                if box:
                    await page.mouse.move(box["x"] + random.uniform(20, 60), box["y"] + random.uniform(20, 50), steps=random.randint(8, 16))
                    await asyncio.sleep(random.uniform(0.4, 0.8))
                await checkbox.click(delay=random.randint(100, 250))
                return True
        except Exception:
            continue
    return False

async def method_1_direct_click(page):
    try:
        challenge_iframe = page.frame_locator('iframe[src*="recaptcha/api2/bframe"]').first
        await page.mouse.move(random.randint(400, 700), random.randint(300, 600), steps=random.randint(6, 12))
        await asyncio.sleep(random.uniform(1.0, 2.0))
        
        audio_btn = challenge_iframe.locator('#recaptcha-audio-button')
        if await audio_btn.is_visible(timeout=5000):
            await audio_btn.click(delay=random.randint(120, 260))
            await asyncio.sleep(random.uniform(2.5, 4.0))

        buster_btn = challenge_iframe.locator('.help-button-holder, button[title*="Solve the challenge"], button[title*="Buster"]').first
        if await buster_btn.is_visible(timeout=5000):
            await buster_btn.click(delay=random.randint(150, 300))
            await asyncio.sleep(random.uniform(7.0, 10.0))
            try:
                verify_btn = challenge_iframe.locator('#recaptcha-verify-button')
                if not await verify_btn.evaluate("node => node.disabled") and await verify_btn.is_visible():
                    await verify_btn.evaluate("node => node.click()")
            except Exception:
                pass
            return True
    except Exception:
        pass
    return False

async def handle_captcha_silent(page):
    if await page.locator('.recaptcha-checkbox-checked').is_visible():
        return True
    if not await page.locator('iframe[src*="recaptcha/api2/bframe"]').is_visible():
        await click_captcha_checkbox(page)
        await asyncio.sleep(random.uniform(2.5, 4.0))
    return await method_1_direct_click(page)

async def click_launch_with_credits_aggressive(page):
    credits_pattern = re.compile(r"Launch\s+with\s+\d+\s+Credit", re.IGNORECASE)
    for _ in range(15):
        await dismiss_popups(page)
        try:
            xpath_loc = page.locator("xpath=//button[contains(text(), 'Launch with') and contains(text(), 'Credit')] | //a[contains(text(), 'Launch with') and contains(text(), 'Credit')]").first
            if await xpath_loc.count() > 0 and await xpath_loc.is_visible():
                if await human_click(page, xpath_loc):
                    await asyncio.sleep(2.5)
                    return True

            text_loc = page.get_by_role("button", name=credits_pattern).first
            if await text_loc.count() > 0 and await text_loc.is_visible():
                if await human_click(page, text_loc):
                    await asyncio.sleep(2.5)
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
                return True
        except Exception:
            pass
        await asyncio.sleep(1)
    return False

async def get_cloud_console_link(page):
    try:
        await page.wait_for_selector('text=Open Google Cloud console', timeout=30000)
        await asyncio.sleep(2)
    except Exception:
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
        if link: return link
    except Exception:
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
                        return href
    except Exception:
        pass
    return None

def resolve_target_region():
    deploy_region = REGION_OVERRIDE
    if "41025" in LAB_URL:
        deploy_region = "us-central1"
    elif "621215" in LAB_URL:
        deploy_region = "europe-west1"
    elif "82384" in LAB_URL:
        deploy_region = REGION_OVERRIDE
    return deploy_region

# ==========================================
# دالة التنفيذ الرئيسية
# ==========================================
async def run():
    raw_cookies = load_cookies_data()
    if not raw_cookies:
        return

    ext_path = await setup_compiled_buster()
    if not ext_path:
        send_user("❌ خطأ أثناء إعداد أدوات المتصفح.")
        return

    user_data_dir = os.path.abspath("chrome_profile")
    max_retries = 3
    success_completely = False

    for attempt in range(1, max_retries + 1):
        if os.path.exists(user_data_dir):
            try: shutil.rmtree(user_data_dir)
            except Exception: pass
        os.makedirs(user_data_dir, exist_ok=True)

        page = None
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

                try:
                    await page.goto(LAB_URL, timeout=30000, wait_until="domcontentloaded")
                except Exception:
                    pass

                await asyncio.sleep(random.uniform(2.5, 4.0))

                # تنظيف الشاشة فوراً عند الدخول وقبل أي عملية فحص أو ضغط على Start
                for _ in range(3):
                    await dismiss_popups(page)
                    await asyncio.sleep(0.5)

                # فحص الجلسة النشطة
                if await check_lab_running_state(page):
                    rem_hours = await extract_remaining_time_hours(page)
                    if rem_hours is not None and rem_hours < 2.0:
                        await end_active_lab(page)
                        await asyncio.sleep(3)
                    else:
                        link = await get_cloud_console_link(page)
                        if link:
                            send_user(f"🎉 <b>تم استخراج رابط الكونسول بنجاح!</b>\n\n🔗 <code>{link}</code>\n\n🚀 <b>جاري إكمال مهمة النشر...</b>")
                            deploy_region = resolve_target_region()
                            await asyncio.sleep(5)
                            await context.close()
                            page = None
                            trigger_github_deploy_task(link, deploy_region)
                            success_completely = True
                            break
                        else:
                            await end_active_lab(page)
                            await asyncio.sleep(3)

                # بدء اللاب من الصفر
                if not success_completely:
                    if await click_start_lab_button(page):
                        await asyncio.sleep(random.uniform(3.0, 4.5))
                        await handle_captcha_silent(page)
                        await asyncio.sleep(random.uniform(2.0, 3.5))

                        if await click_launch_with_credits_aggressive(page):
                            await asyncio.sleep(random.uniform(4.0, 6.0))
                            link = await get_cloud_console_link(page)
                            if link:
                                send_user(f"🎉 <b>تم بدء اللاب بنجاح!</b>\n\n🔗 <code>{link}</code>\n\n🚀 <b>جاري إكمال مهمة النشر...</b>")
                                deploy_region = resolve_target_region()
                                await asyncio.sleep(5)
                                await context.close()
                                page = None
                                trigger_github_deploy_task(link, deploy_region)
                                success_completely = True
                            else:
                                await page.screenshot(path="err_no_link.png", full_page=True)
                                send_admin(f"⚠️ فشل سحب الرابط بعد البدء (محاولة {attempt}) - مستخدم: {CHAT_ID}", "err_no_link.png")
                        else:
                            await page.screenshot(path="err_launch.png", full_page=True)
                            send_admin(f"❌ فشل زر Launch with Credit (محاولة {attempt}) - مستخدم: {CHAT_ID}", "err_launch.png")
                    else:
                        await page.screenshot(path="err_start.png", full_page=True)
                        send_admin(f"❌ فشل زر Start Lab (محاولة {attempt}) - مستخدم: {CHAT_ID}", "err_start.png")

            except Exception as e:
                if page:
                    try:
                        await page.screenshot(path="err_crash.png", full_page=True)
                        send_admin(f"🔥 كراش في المحاولة ({attempt}) للمستخدم: {CHAT_ID}\n<code>{e}</code>", "err_crash.png")
                    except Exception:
                        send_admin(f"🔥 كراش في المحاولة ({attempt}) للمستخدم: {CHAT_ID}\n<code>{e}</code>")
            finally:
                if page:
                    try: await context.close()
                    except Exception: pass

        if success_completely:
            break
        else:
            if attempt < max_retries:
                send_user(f"⚠️ فشلت المحاولة ({attempt})، جاري إعادة المحاولة...")
                await asyncio.sleep(8)
            else:
                send_user("❌ <b>فشل بدء اللاب بعد استنفاد جميع المحاولات.</b>")
                send_admin(f"❌ انتهت كافة المحاولات (3/3) بالفشل للمستخدم: <code>{CHAT_ID}</code>")

if __name__ == "__main__":
    asyncio.run(run())
