import asyncio
import os
import zipfile
import requests
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ========== إعدادات التيليجرام ==========
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
# =====================================

LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

# دمج كوكيز Google العامة مع كوكيز skills.google
MY_COOKIES = [
    # كوكيز skills.google
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

async def wait_and_click_start_lab(page):
    """انتظار والنقر على زر Start Lab بالطريقة الصحيحة"""
    send_tg("🔍 جاري البحث عن زر Start Lab...")
    
    # محددات محددة للزر الأخضر في Google Skills
    selectors = [
        'button:has-text("Start Lab")',
        'button:has-text("START LAB")',
        'button.ql-button--primary',  # غالباً يستخدم هذا الكلاس
        'button.start-lab-button',
        '[data-testid="start-lab-button"]',
        'button:has-text("Start")',
        'button.ql-button',
        'button.mdc-button--raised',  # مادة تصميم Google
        '//button[contains(., "Start Lab")]',  # XPath
        '//button[contains(., "START LAB")]',
    ]
    
    clicked = False
    
    for selector in selectors:
        try:
            # انتظار ظهور الزر والتحقق من أنه مرئي وقابل للنقر
            if selector.startswith('//'):
                # XPath
                locator = page.locator(f"xpath={selector}")
            else:
                locator = page.locator(selector)
            
            # انتظار حتى يكون الزر مرئياً وقابلاً للنقر
            await locator.first.wait_for(state="visible", timeout=5000)
            
            # التحقق من أن الزر يحتوي على النص الصحيح (للتأكد)
            count = await locator.count()
            for i in range(count):
                btn = locator.nth(i)
                if await btn.is_visible() and await btn.is_enabled():
                    text = await btn.text_content() or ""
                    if "start" in text.lower() or "lab" in text.lower() or "بدء" in text:
                        # التمرير إلى الزر
                        await btn.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        
                        # محاولة النقر العادي أولاً
                        try:
                            await btn.click(timeout=5000)
                            clicked = True
                            send_tg(f"✅ تم النقر على الزر باستخدام المحدد: {selector}")
                            return True
                        except:
                            # إذا فشل، استخدام JavaScript
                            await btn.evaluate("element => element.click()")
                            clicked = True
                            send_tg(f"✅ تم النقر على الزر باستخدام JavaScript: {selector}")
                            return True
                        
        except PlaywrightTimeout:
            continue
        except Exception as e:
            print(f"محاولة فاشلة مع {selector}: {e}")
            continue
    
    # محاولة أخيرة: البحث في جميع الأزرار
    if not clicked:
        try:
            buttons = await page.query_selector_all('button')
            for btn in buttons:
                text = await btn.text_content()
                if text and ("start lab" in text.lower() or "start" in text.lower()):
                    await btn.scroll_into_view_if_needed()
                    await btn.click()
                    send_tg("✅ تم النقر على الزر بالبحث في جميع الأزرار")
                    return True
        except Exception as e:
            send_tg(f"⚠️ فشل في النقر على الزر: {str(e)[:100]}")
    
    return False

async def handle_recaptcha(page):
    """معالجة reCAPTCHA بشكل صحيح"""
    try:
        # البحث عن iframe الكابتشا
        recaptcha_frame = None
        
        for frame in page.frames:
            if "recaptcha" in frame.url:
                recaptcha_frame = frame
                break
        
        if not recaptcha_frame:
            return False
        
        send_tg("🤖 تم اكتشاف reCAPTCHA")
        
        # محاولة النقر على checkbox
        try:
            checkbox = recaptcha_frame.locator(".recaptcha-checkbox-border")
            await checkbox.click(timeout=10000)
            send_tg("✅ تم النقر على checkbox")
            await asyncio.sleep(5)
        except:
            pass
        
        # التحقق مما إذا كان هناك تحدي صوتي
        try:
            # البحث عن iframe التحدي
            challenge_frame = None
            for frame in page.frames:
                if "api2/bframe" in frame.url or "recaptcha/api2/bframe" in frame.url:
                    challenge_frame = frame
                    break
            
            if challenge_frame:
                send_tg("🔊 التحدي الصوتي ظهر، جاري استخدام Buster...")
                
                # محاولة النقر على زر الصوت
                audio_btn = challenge_frame.locator("#recaptcha-audio-button")
                await audio_btn.click(timeout=5000)
                await asyncio.sleep(2)
                
                # النقر على زر Buster إذا وجد
                try:
                    buster_btn = challenge_frame.locator("#solver-button")
                    await buster_btn.click(timeout=10000)
                    send_tg("🎯 تم تفعيل Buster")
                    await asyncio.sleep(15)  # انتظار الحل
                except:
                    send_tg("⚠️ لم يتم العثور على زر Buster")
                    
        except Exception as e:
            print(f"خطأ في معالجة التحدي: {e}")
            
        return True
        
    except Exception as e:
        print(f"خطأ في معالجة الكابتشا: {e}")
        return False

async def check_lab_status(page):
    """التحقق من حالة اللاب بعد الضغط"""
    try:
        # انتظار إما ظهور المهام أو تغير URL
        await asyncio.sleep(3)
        
        # التحقق من وجود Task 1 أو محتوى المختبر
        content = await page.content()
        
        if "Task 1" in content or "task 1" in content.lower():
            send_tg("📋 اللاب يعمل - تم اكتشاف المهام")
            return True
            
        if "console.cloud.google.com" in page.url:
            send_tg("☁️ تم التحويل إلى Google Cloud Console")
            return True
            
        # التحقق من وجود عناصر المختبر
        try:
            await page.wait_for_selector("text=/Task \\d|Open Google Console|Credentials/i", timeout=10000)
            send_tg("✅ تم تأكيد بدء اللاب")
            return True
        except:
            pass
            
        return False
        
    except Exception as e:
        print(f"خطأ في التحقق: {e}")
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
                "--window-size=1366,768",
                "--start-maximized"
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768'},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()
        
        try:
            send_tg("🌐 فتح صفحة اللاب...")
            
            # الانتقال للصفحة مع انتظار التحميل الكامل
            response = await page.goto(LAB_URL, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_load_state("networkidle")
            
            await asyncio.sleep(3)
            
            # التقاط صورة أولية
            await page.screenshot(path="lab_page.png")
            send_tg("📸 صفحة اللاب مفتوحة", "lab_page.png")
            
            # الضغط على زر Start Lab
            clicked = await wait_and_click_start_lab(page)
            
            if clicked:
                await asyncio.sleep(3)
                
                # التحقق من ظهور الكابتشا
                await handle_recaptcha(page)
                
                # انتظار وتحقق من حالة اللاب
                success = await check_lab_status(page)
                
                await asyncio.sleep(5)
                await page.screenshot(path="after_start.png")
                
                if success:
                    send_tg("✅ اللاب يعمل بنجاح", "after_start.png")
                else:
                    send_tg("⚠️ تم الضغط على الزر لكن الحالة غير مؤكدة", "after_start.png")
            else:
                send_tg("❌ فشل في الضغط على زر Start Lab")
                # محاولة التحقق إذا كان اللاب قد بدأ بالفعل
                if await check_lab_status(page):
                    send_tg("✅ اللاب يعمل بالفعل!")
            
            # صورة نهائية كاملة
            await page.screenshot(path="final.png", full_page=True)
            final_url = page.url
            send_tg(f"🏁 المهمة انتهت\n🔗 الرابط: {final_url}", "final.png")
            
        except Exception as e:
            error_msg = str(e)
            send_tg(f"❌ خطأ: {error_msg[:200]}")
            try:
                await page.screenshot(path="error.png", full_page=True)
                send_tg("📸 لقطة الخطأ", "error.png")
            except:
                pass
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
