import asyncio
import os
import requests
import zipfile
from playwright.async_api import async_playwright

# --- إعداداتك الخاصة ---
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "5813081202"
# ⚠️ لا تنسَ وضع إيميلك وكلمة السر هنا:
EMAIL_USER = "ضع_إيميلك_هنا@gmail.com" 
EMAIL_PASS = "ضع_كلمة_سر_الإيميل_هنا"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

def send_telegram(text, photo_path=None):
    """إرسال رسائل أو صور إلى تليجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": text}, files={"photo": photo})
        else:
            requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print(f"Telegram Error: {e}")

async def download_buster():
    """استخراج أحدث إصدار لإضافة Buster من قسم Releases في GitHub تلقائياً"""
    print("جاري البحث عن أحدث إصدار لإضافة Buster من GitHub...")
    
    # واجهة برمجة التطبيقات لجلب أحدث إصدار من المستودع الذي أرسلته
    api_url = "https://api.github.com/repos/dessant/buster/releases/latest"
    response = requests.get(api_url).json()
    
    download_url = None
    # نبحث عن الملف الجاهز للمتصفح (ينتهي بـ .zip وفيه كلمة chrome)
    for asset in response.get("assets", []):
        if "chrome" in asset["name"].lower() and asset["name"].endswith(".zip"):
            download_url = asset["browser_download_url"]
            break
            
    if not download_url:
        raise Exception("لم يتم العثور على رابط التحميل الجاهز في صفحة GitHub!")
        
    print(f"تم العثور على الرابط، جاري التحميل: {download_url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    r = requests.get(download_url, headers=headers)
    
    # التأكد أن الملف سليم ويبدأ بترميز ملفات Zip (PK)
    if r.status_code == 200 and r.content.startswith(b'PK'):
        with open("buster.zip", "wb") as f:
            f.write(r.content)
        print("تم التحميل. جاري فك الضغط...")
        with zipfile.ZipFile("buster.zip", "r") as zip_ref:
            zip_ref.extractall("buster_ext")
        return os.path.abspath("buster_ext")
    else:
        raise Exception("الملف المحمل ليس بصيغة zip صالحة.")

async def run_task():
    try:
        ext_path = await download_buster()
    except Exception as e:
        send_telegram(f"❌ خطأ في تحميل الإضافة: {str(e)}")
        return

    async with async_playwright() as p:
        # تشغيل المتصفح وتحميل الإضافة
        context = await p.chromium.launch_persistent_context(
            "user_data_profile",
            headless=False, # الإضافات تحتاج واجهة، وسنستخدم xvfb في Github Actions
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        page = context.pages[0]

        try:
            # 1. تسجيل الدخول إلى جوجل
            print("جاري تسجيل الدخول إلى جوجل...")
            await page.goto("https://accounts.google.com/ServiceLogin", wait_until="networkidle")
            await page.fill('input[type="email"]', EMAIL_USER)
            await page.keyboard.press("Enter")
            await asyncio.sleep(4)
            await page.fill('input[type="password"]', EMAIL_PASS)
            await page.keyboard.press("Enter")
            await asyncio.sleep(8) 

            # 2. الذهاب إلى صفحة جوجل سكيلز
            print("الانتقال إلى Google Skills...")
            await page.goto("https://www.cloudskillsboost.google/", wait_until="networkidle")
            
            try:
                # محاولة الضغط على Join إذا لم يكن مسجلاً تلقائياً
                if await page.get_by_role("button", name="Join").is_visible():
                    await page.get_by_role("button", name="Join").click()
                    await asyncio.sleep(2)
                    await page.click("text=Sign in with Google")
                    await asyncio.sleep(5)
            except: pass

            # 3. الدخول إلى اللاب
            print("الانتقال لرابط اللاب...")
            await page.goto(LAB_URL, wait_until="networkidle")
            
            # الضغط على زر Start Lab
            start_btn = page.locator("button:has-text('Start Lab')").first
            await start_btn.click()
            await asyncio.sleep(5)

            # 4. التعامل مع الكبتشا وتفعيل إضافة Buster
            print("البحث عن الكبتشا لحلها...")
            captcha_frame = None
            for frame in page.frames:
                # إطار مربع "أنا لست روبوت"
                if "google.com/recaptcha/api2/anchor" in frame.url:
                    captcha_frame = frame
                    break
            
            if captcha_frame:
                await captcha_frame.click(".recaptcha-checkbox-border")
                await asyncio.sleep(4) # انتظار ظهور صور التحدي
                
                # البحث عن إطار التحدي الذي تزرع فيه Buster زرها
                buster_frame = None
                for frame in page.frames:
                    if "api2/bframe" in frame.url:
                        buster_frame = frame
                        break
                
                if buster_frame:
                    print("تم العثور على نافذة التحدي، جاري النقر على أيقونة Buster...")
                    # زر Buster يحمل هذا الـ ID عادة
                    await buster_frame.click("#solver-button")
                    print("تم النقر! ننتظر 10 ثوانٍ ليتم الحل الآلي...")
                    await asyncio.sleep(12) 

            # 5. انتظار تفعيل اللاب
            print("انتظار تفعيل اللاب وتجهيز السيرفر...")
            await asyncio.sleep(15)
            final_url = page.url
            
            send_telegram(f"✅ تم تشغيل اللاب بنجاح!\nرابط اللاب: {final_url}")
            print("العملية اكتملت بنجاح.")

        except Exception as e:
            # في حال وجود خطأ، نصور الشاشة ونرسلها للتلجرام لمعرفة السبب
            await page.screenshot(path="error_trace.png")
            send_telegram(f"❌ حدث خطأ أثناء تشغيل اللاب:\n{str(e)[:200]}", photo_path="error_trace.png")
            print(f"Error occurred: {e}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_task())
