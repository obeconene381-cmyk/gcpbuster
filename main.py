import asyncio
import os
import requests
import zipfile
from playwright.async_api import async_playwright

# --- تكوين التلجرام وحساب Google ---
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "5813081202"
# ملاحظة: استبدل بالقيم الفعلية لحسابك
EMAIL_USER = "omarcora02@gmail.com" 
EMAIL_PASS = "omar@2008"        

def send_telegram(text, photo_path=None):
    """إرسال رسالة نصية أو صورة إلى التلجرام."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, "rb") as photo:
            try:
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID, "caption": text}, files={"photo": photo})
            except Exception as e:
                requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": f"{text}\n\n(فشل إرسال الصورة: {e})"})
    else:
        requests.post(url + "sendMessage", json={"chat_id": CHAT_ID, "text": text})

async def download_and_extract_buster():
    """يحمل إضافة Buster كملف zip ويفك ضغطها، ويعيد المسار الكامل للمجلد."""
    # رابط تحميل مباشر لأحدث إصدار من Buster (نسخة متوافقة مع Chromium)
    # ملاحظة: قد يحتاج الرابط لتحديث إذا تغير إصدار الإضافة
    buster_url = "https://github.com/dessant/buster/releases/download/v2.0.1/buster-chrome-2.0.1.zip"
    buster_zip_path = "buster.zip"
    buster_ext_path = "buster_ext"

    # 1. تحميل ملف الـ zip
    if not os.path.exists(buster_zip_path):
        print("جاري تحميل إضافة Buster...")
        r = requests.get(buster_url)
        with open(buster_zip_path, "wb") as f:
            f.write(r.content)
        print("تم التحميل.")

    # 2. فك الضغط
    if not os.path.exists(buster_ext_path):
        print("جاري فك ضغط الإضافة...")
        with zipfile.ZipFile(buster_zip_path, "r") as zip_ref:
            zip_ref.extractall(buster_ext_path)
        print("تم فك الضغط.")

    # إعادة المسار المطلق لمجلد الإضافة
    return os.path.abspath(buster_ext_path)

async def run_automation():
    """تقوم بتشغيل الأتمتة الكاملة."""
    # 1. الحصول على مسار الإضافة
    ext_path = await download_and_extract_buster()
    print(f"مسار الإضافة المحملة: {ext_path}")

    async with async_playwright() as p:
        # 2. تشغيل المتصفح بوضع Persistent Context وتحميل الإضافة
        # هذا هو التكوين الضروري لتشغيل الإضافات
        print("جاري تشغيل المتصفح مع الإضافة...")
        # نترك مسار user_data_dir فارغاً لإنشاء بروفايل مؤقت جديد في كل مرة
        context = await p.chromium.launch_persistent_context(
            "", # user_data_dir: مسار لتخزين بيانات المستخدم (مؤقت هنا)
            headless=False, # الإضافات لا تعمل في وضع Headless
            args=[
                f"--disable-extensions-except={ext_path}", # تحميل الإضافة المحددة فقط
                f"--load-extension={ext_path}", # تحميل الإضافة
                "--no-sandbox", # ضروري لـ GitHub Actions
                "--disable-gpu" # قد يساعد في بعض البيئات
            ]
        )
        
        # الحصول على الصفحة الأولى (يتم فتحها تلقائياً عند launch_persistent_context)
        page = context.pages[0]

        try:
            # 3. الأتمتة: تسجيل الدخول وبدء اللاب
            # الدخول إلى جوجل سكيلز لبدء عملية تسجيل الدخول
            print("جاري الدخول إلى Google Skills Boost...")
            await page.goto("https://www.cloudskillsboost.google/", wait_until="networkidle")
            
            # النقر على Join
            join_btn = page.locator("a.qed-button:has-text('Join')").first
            await join_btn.click()
            await asyncio.sleep(2)

            # تسجيل الدخول عبر جوجل
            print("جاري بدء تسجيل الدخول بحساب Google...")
            await page.click("text=Sign in with Google")
            
            # إدخال الإيميل
            await page.fill('input[type="email"]', EMAIL_USER)
            await page.click("#identifierNext")
            await asyncio.sleep(3)
            
            # إدخال الباسورد
            await page.fill('input[type="password"]', EMAIL_PASS)
            await page.click("#passwordNext")
            await asyncio.sleep(10) # انتظار طويل لتخطي التحققات الأمنية المحتملة

            # التوجه إلى رابط اللاب
            lab_url = "https://www.skills.google/focuses/19146?parent=catalog"
            print(f"جاري الانتقال إلى رابط اللاب: {lab_url}")
            await page.goto(lab_url, wait_until="networkidle")

            # الضغط على "Start Lab"
            print("جاري الضغط على Start Lab...")
            start_btn = page.locator("button:has-text('Start Lab')")
            await start_btn.click()
            await asyncio.sleep(5)

            # 4. التعامل مع الكبتشا (Buster)
            # البحث عن iframe الكبتشا
            captcha_frame = None
            for frame in page.frames:
                if "google.com/recaptcha" in frame.url:
                    captcha_frame = frame
                    break
            
            if captcha_frame:
                print("تم اكتشاف الكبتشا، جاري محاولة الحل...")
                # الضغط على مربع "أنا لست روبوت"
                await captcha_frame.click(".recaptcha-checkbox-border")
                await asyncio.sleep(3)
                
                # الآن يظهر مربع التحدي، نبحث عن زر Buster
                bframe = None
                for frame in page.frames:
                    if "api2/bframe" in frame.url:
                        bframe = frame
                        break
                
                if bframe:
                    print("جاري الضغط على زر Buster لحل الكبتشا...")
                    # الضغط على أيقونة Buster (تظهر كزر حل)
                    await bframe.click("#solver-button")
                    await asyncio.sleep(10) # انتظار أطول للإضافة لحل الكبتشا

            # 5. إنهاء المهمة وإرسال الرابط
            print("انتظار بدء اللاب ونسخ الرابط...")
            await asyncio.sleep(15) # انتظار إضافي لبدء اللاب فعلياً
            current_url = page.url
            print(f"تم الحصول على رابط اللاب: {current_url}")
            send_telegram(f"✅ تم بدء اللاب بنجاح!\nرابط اللاب الحالي: {current_url}")

        except Exception as e:
            print(f"حدث خطأ: {e}")
            screenshot_path = "error.png"
            await page.screenshot(path=screenshot_path)
            send_telegram(f"❌ حدث خطأ أثناء الأتمتة: {str(e)}", photo_path=screenshot_path)
        finally:
            print("جاري إغلاق المتصفح.")
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_automation())
