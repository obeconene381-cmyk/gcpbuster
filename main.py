import asyncio
import os
import requests
from playwright.async_api import async_playwright

BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"

def send_telegram_photo(photo_path, caption):
    print(f"جاري إرسال الصورة: {photo_path}...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        if os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": photo})
            print("تم إرسال الصورة بنجاح!")
    except Exception as e:
        print(f"❌ خطأ في إرسال التلجرام: {e}")

async def run_automation():
    async with async_playwright() as p:
        print("جاري تشغيل المتصفح...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir="/tmp/playwright_user_data",
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = context.pages[0]

        try:
            extension_url = "https://chrome.google.com/webstore/detail/buster-captcha-solver-for/mpbjkejclgfgadiemmefgebjfooflfhl?hl=en"
            print("الانتقال إلى متجر كروم...")
            await page.goto(extension_url, wait_until="networkidle")
            await asyncio.sleep(5)

            print("محاولة الضغط على زر الإضافة...")
            add_button = page.locator("button:has-text('Add to Chrome')").first
            if await add_button.is_visible():
                await add_button.click()
                print("تم الضغط على زر الإضافة.")
            
            # --- التعديل هنا: زيادة وقت الانتظار بشكل كبير ---
            print("ننتظر الآن 10 ثوانٍ كاملة لإعطاء المتصفح فرصة للتحميل...")
            await asyncio.sleep(10) 

            final_store_path = "store_result.png"
            await page.screenshot(path=final_store_path, full_page=True)
            send_telegram_photo(final_store_path, "1. صورة المتجر بعد الانتظار 10 ثوانٍ (لاحظ الدائرة التي لا تزال تدور)")

            print("الانتقال لصفحة الإضافات الداخلية...")
            await page.goto("chrome://extensions/")
            await asyncio.sleep(5)
            ext_list_path = "extensions_check.png"
            await page.screenshot(path=ext_list_path, full_page=True)
            send_telegram_photo(ext_list_path, "2. صفحة الإضافات (ستجدها فارغة للأسف)")

        except Exception as e:
            await page.screenshot(path="error.png")
            send_telegram_photo("error.png", f"❌ حدث خطأ:\n{str(e)[:150]}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_automation())

        try:
            # 1. الدخول إلى رابط الإضافة في متجر كروم
            extension_url = "https://chrome.google.com/webstore/detail/buster-captcha-solver-for/mpbjkejclgfgadiemmefgebjfooflfhl?hl=en"
            print("الانتقال إلى متجر كروم...")
            await page.goto(extension_url, wait_until="networkidle")
            await asyncio.sleep(5)

            # 2. الضغط على زر "Add to Chrome"
            print("محاولة الضغط على زر الإضافة...")
            add_button = page.locator("button:has-text('Add to Chrome')").first
            if await add_button.is_visible():
                await add_button.click()
                print("تم الضغط على زر الإضافة.")
            else:
                print("الزر غير موجود، قد تكون الإضافة مثبتة بالفعل.")

            # 3. الانتظار (هنا تظهر نافذة التأكيد التي لا يمكن للبوت النقر عليها يدوياً)
            print("انتظار 15 ثانية لرؤية النتيجة النهائية...")
            await asyncio.sleep(15)

            # 4. التقاط صورة لصفحة المتجر بعد المحاولة
            final_store_path = "store_result.png"
            await page.screenshot(path=final_store_path, full_page=True)
            send_telegram_photo(final_store_path, "1. حالة صفحة المتجر بعد الضغط على الزر (تأكد هل تغير النص إلى Remove من Chrome؟)")

            # 5. التوجه لصفحة الإضافات الداخلية للتأكد اليقيني (الدليل القاطع)
            print("الانتقال لصفحة الإضافات الداخلية...")
            await page.goto("chrome://extensions/")
            await asyncio.sleep(5)
            ext_list_path = "extensions_check.png"
            await page.screenshot(path=ext_list_path, full_page=True)
            send_telegram_photo(ext_list_path, "2. دليل قاطع: هذه هي قائمة الإضافات المثبتة فعلياً داخل المتصفح الآن.")

        except Exception as e:
            await page.screenshot(path="error.png")
            send_telegram_photo("error.png", f"❌ حدث خطأ أثناء المحاكاة:\n{str(e)[:150]}")
            print(f"Error: {e}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_automation())
