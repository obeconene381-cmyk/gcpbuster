import asyncio
import os
import requests
from playwright.async_api import async_playwright

# --- إعدادات التلجرام ---
BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "5813081202"

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

async def run_automation():
    async with async_playwright() as p:
        # تشغيل المتصفح (Headless=False لكي تتمكن الإضافات من العمل إن وجدت)
        print("جاري تشغيل المتصفح...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir="/tmp/playwright_user_data",
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = context.pages[0]

        try:
            # 1. الدخول إلى رابط الإضافة في متجر كروم
            extension_url = "https://chrome.google.com/webstore/detail/buster-captcha-solver-for/mpbjkejclgfgadiemmefgebjfooflfhl?hl=en"
            print("الانتقال إلى متجر كروم...")
            await page.goto(extension_url, wait_until="networkidle")
            await asyncio.sleep(5)

            # 2. البحث عن زر "Add to Chrome" والضغط عليه
            print("البحث عن زر الإضافة...")
            
            # المتجر قد يحتوي على عدة أزرار، سنستهدف الزر الذي يحتوي على النص المطلوب
            try:
                add_button = page.locator("button:has-text('Add to Chrome')").first
                await add_button.wait_for(state="visible", timeout=10000)
                await add_button.click()
                print("تم الضغط على 'Add to Chrome' بنجاح!")
            except Exception as e:
                print("لم يتم العثور على زر 'Add to Chrome'. قد يكون المتجر معروضاً بلغة أخرى.")
                # محاولة باللغة العربية كبديل
                try:
                    add_button_ar = page.locator("button:has-text('إضافة إلى Chrome')").first
                    await add_button_ar.click()
                    print("تم الضغط على 'إضافة إلى Chrome' باللغة العربية!")
                except:
                    raise Exception("لم نتمكن من إيجاد زر الإضافة.")

            # 3. محاولة أخذ سكرين شوت (هنا ستتوقف العملية ولن يستطيع المتصفح إكمال التأكيد)
            print("في هذه اللحظة ظهرت نافذة التأكيد المنبثقة من المتصفح.")
            print("ملاحظة: Playwright لا يستطيع النقر على 'Add extension' في هذه النافذة.")
            
            await asyncio.sleep(10) # ننتظر 10 ثوانٍ لترى ماذا سيحدث
            
            await page.screenshot(path="webstore_attempt.png")
            send_telegram("⚠️ تم الدخول للمتجر والضغط على 'Add to Chrome'. شاهد السكرين شوت (النافذة المنبثقة لا تظهر في الصور عادة).", "webstore_attempt.png")

        except Exception as e:
            await page.screenshot(path="error.png")
            send_telegram(f"❌ خطأ أثناء تجربة المتجر:\n{str(e)[:150]}", "error.png")
            print(f"Error: {e}")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_automation())
