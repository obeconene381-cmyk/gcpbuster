import asyncio
import os
import requests
from playwright.async_api import async_playwright

# بيانات التلجرام
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"

# بيانات حساب جوجل
EMAIL_USER = "omarcora02"
EMAIL_PASS = "omar@2008"

def send_telegram_photo(photo_path, caption):
    print(f"جاري إرسال الصورة: {photo_path}...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        if os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": photo})
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
            # 1. تسجيل الدخول إلى حساب جوجل أولاً
            print("جاري تسجيل الدخول لحساب جوجل...")
            await page.goto("https://accounts.google.com/ServiceLogin", wait_until="networkidle")
            
            await page.fill('input[type="email"]', EMAIL_USER)
            await page.keyboard.press("Enter")
            await asyncio.sleep(4) # انتظار انتقال الصفحة
            
            await page.fill('input[type="password"]', EMAIL_PASS)
            await page.keyboard.press("Enter")
            await asyncio.sleep(8) # انتظار إتمام تسجيل الدخول

            # 2. الانتقال إلى متجر كروم بعد تسجيل الدخول
            extension_url = "https://chrome.google.com/webstore/detail/buster-captcha-solver-for/mpbjkejclgfgadiemmefgebjfooflfhl?hl=en"
            print("الانتقال إلى متجر كروم...")
            await page.goto(extension_url, wait_until="networkidle")
            await asyncio.sleep(5)

            # 3. محاولة الضغط على زر الإضافة
            print("محاولة الضغط على زر الإضافة...")
            add_button = page.locator("button:has-text('Add to Chrome')").first
            if await add_button.is_visible():
                await add_button.click()
                print("تم الضغط على زر الإضافة.")
            
            print("ننتظر الآن 10 ثوانٍ كاملة...")
            await asyncio.sleep(10) 

            # 4. التقاط صورة للنتيجة
            final_store_path = "store_result.png"
            await page.screenshot(path=final_store_path, full_page=True)
            send_telegram_photo(final_store_path, "النتيجة بعد تسجيل الدخول ومحاولة الإضافة من المتجر")

        except Exception as e:
            await page.screenshot(path="error.png")
            send_telegram_photo("error.png", f"❌ حدث خطأ:\n{str(e)[:150]}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_automation())
