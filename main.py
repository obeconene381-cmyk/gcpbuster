import asyncio
import os
import requests
import zipfile
import shutil
from playwright.async_api import async_playwright

# ==========================================
# ضع بياناتك هنا
# ==========================================
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "5813081202"
EMAIL_USER = "ضع_ايميلك_هنا@gmail.com" 
EMAIL_PASS = "ضع_كلمة_السر_هنا"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

def send_telegram(text, photo_path=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": text}, files={"photo": photo})
        else:
            requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print(f"Telegram Error: {e}")

async def setup_buster_extension():
    """تحميل إضافة Buster أحدث إصدار وتجهيزها"""
    print("جاري تحميل إضافة Buster (إصدار 3.1.1)...")
    buster_url = "https://github.com/dessant/buster/releases/download/v3.1.1/buster-chrome-3.1.1.zip"
    zip_name = "buster_latest.zip"
    ext_dir = "buster_extension"

    # تحميل الملف
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(buster_url, headers=headers)
    
    # التأكد من أن الملف سليم (ملفات zip تبدأ بـ PK)
    if response.status_code == 200 and response.content.startswith(b'PK'):
        with open(zip_name, "wb") as f:
            f.write(response.content)
        print("تم التحميل بنجاح. جاري فك الضغط...")
        
        # تنظيف المجلد القديم إن وجد
        if os.path.exists(ext_dir):
            shutil.rmtree(ext_dir)
            
        with zipfile.ZipFile(zip_name, "r") as zip_ref:
            zip_ref.extractall(ext_dir)
        return os.path.abspath(ext_dir)
    else:
        raise Exception("فشل تحميل ملف الإضافة الصحيح. الرابط قد يكون معطلاً.")

async def run_automation():
    # 1. تجهيز الإضافة
    ext_path = await setup_buster_extension()

    async with async_playwright() as p:
        # 2. فتح المتصفح مع الإضافة المحملة
        print("تشغيل المتصفح...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir="/tmp/playwright_user_data",
            headless=False, # ضروري لكي تعمل الإضافات
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        page = context.pages[0]

        try:
            # 3. تسجيل الدخول إلى إيميل جوجل (كما في الفيديو)
            print("جاري الدخول لحساب جوجل...")
            await page.goto("https://accounts.google.com/ServiceLogin", wait_until="networkidle")
            
            await page.wait_for_selector('input[type="email"]')
            await page.fill('input[type="email"]', EMAIL_USER)
            await page.keyboard.press("Enter")
            
            await page.wait_for_selector('input[type="password"]', state="visible", timeout=10000)
            await asyncio.sleep(2) # انتظار لضمان ظهور الحقل بالكامل
            await page.fill('input[type="password"]', EMAIL_PASS)
            await page.keyboard.press("Enter")
            await asyncio.sleep(5) 

            # 4. الدخول إلى رابط جوجل سكيلز
            print("الانتقال إلى موقع جوجل سكيلز...")
            await page.goto("https://www.cloudskillsboost.google/", wait_until="networkidle")
            
            # محاولة تسجيل الدخول هناك إذا لزم الأمر
            try:
                if await page.locator("text=Join").is_visible():
                    await page.click("text=Join")
                    await asyncio.sleep(2)
                    await page.click("text=Sign in with Google")
                    await asyncio.sleep(5)
            except: pass

            # 5. الدخول إلى اللاب وتخطي الكبتشا
            print("الانتقال إلى اللاب للبدء...")
            await page.goto(LAB_URL, wait_until="networkidle")
            
            # النقر على زر Start Lab (الزر الأخضر)
            await page.click("button:has-text('Start Lab')")
            print("تم النقر على بدء اللاب، ننتظر الكبتشا...")
            await asyncio.sleep(4)

            # البحث عن الكبتشا والنقر على مربع "أنا لست روبوت"
            captcha_frame = None
            for frame in page.frames:
                if "google.com/recaptcha/api2/anchor" in frame.url:
                    captcha_frame = frame
                    break
            
            if captcha_frame:
                await captcha_frame.click(".recaptcha-checkbox-border")
                await asyncio.sleep(3)
                
                # البحث عن نافذة الصور (التحدي) والنقر على إضافة Buster (الزر البرتقالي/الأصفر)
                buster_frame = None
                for frame in page.frames:
                    if "api2/bframe" in frame.url:
                        buster_frame = frame
                        break
                
                if buster_frame:
                    print("تم ظهور الصور، جاري النقر على إضافة تخطي الكبتشا...")
                    await buster_frame.click("#solver-button")
                    print("تم النقر على الإضافة. جاري الحل...")
                    await asyncio.sleep(10) # انتظار الإضافة لتنفيذ عملها

            # 6. انتظار بدء اللاب ونسخ الرابط
            print("انتظار 5 ثواني لبدء اللاب الفعلي...")
            await asyncio.sleep(5)
            
            final_url = page.url
            print("اكتملت المهمة!")
            send_telegram(f"✅ تم بدء اللاب وتخطي الكبتشا بنجاح!\nالرابط الحالي: {final_url}")

        except Exception as e:
            await page.screenshot(path="error.png")
            send_telegram(f"❌ حدث خطأ:\n{str(e)[:150]}", photo_path="error.png")
            print(f"Error: {e}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_automation())
