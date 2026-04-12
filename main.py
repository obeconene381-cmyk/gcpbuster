import asyncio
import os
import zipfile
import requests
from playwright.async_api import async_playwright

BOT_TOKEN = "8676477338:AAHTkfqD5p2RV0-d8QetCY4Bs9RDgsaWFDU"
CHAT_ID = "8092953314"
LAB_URL = "https://www.skills.google/focuses/19146?parent=catalog"

MY_COOKIES = [
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

async def click_start_lab_simple(page):
    """طريقة بسيطة ومباشرة للنقر على Start Lab"""
    
    send_tg("🔍 البحث عن Start Lab...")
    
    # طريقة 1: البحث بالـ Playwright locator
    try:
        # انتظار ظهور الزر
        await page.wait_for_selector('text=Start Lab', timeout=10000)
        
        # النقر على الزر
        await page.click('text=Start Lab', force=True)
        send_tg("✅ تم النقر (طريقة 1: text selector)")
        return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 1 فشلت: {str(e)[:100]}")
    
    # طريقة 2: XPath
    try:
        await page.click('xpath=//button[contains(text(), "Start Lab")]', force=True)
        send_tg("✅ تم النقر (طريقة 2: XPath)")
        return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 2 فشلت: {str(e)[:100]}")
    
    # طريقة 3: JavaScript بسيط
    try:
        result = await page.evaluate("""
            () => {
                // البحث عن جميع الأزرار والروابط
                const elements = document.querySelectorAll('button, a, [role="button"]');
                
                for (const el of elements) {
                    const text = (el.innerText || el.textContent || '').toLowerCase().trim();
                    
                    if (text === 'start lab' || text.includes('start lab')) {
                        // التمرير
                        el.scrollIntoView({block: 'center', behavior: 'instant'});
                        
                        // النقر
                        el.click();
                        
                        return {
                            success: true, 
                            tag: el.tagName,
                            text: el.innerText?.substring(0, 50),
                            class: el.className
                        };
                    }
                }
                
                return {success: false, reason: 'Not found'};
            }
        """)
        
        if result.get('success'):
            send_tg(f"✅ تم النقر (طريقة 3: JS) - {result.get('tag')} | {result.get('text')}")
            return True
        else:
            send_tg(f"⚠️ طريقة 3: {result.get('reason')}")
    except Exception as e:
        send_tg(f"⚠️ طريقة 3 فشلت: {str(e)[:100]}")
    
    # طريقة 4: النقر على الإحداثيات (من الصورة الزر حوالي x=100, y=200)
    try:
        await page.mouse.click(120, 220)
        send_tg("✅ تم النقر (طريقة 4: coordinates guess)")
        return True
    except Exception as e:
        send_tg(f"⚠️ طريقة 4 فشلت: {e}")
    
    return False

async def handle_recaptcha(page):
    """معالجة reCAPTCHA"""
    try:
        await asyncio.sleep(2)
        
        for frame in page.frames:
            if "recaptcha" in frame.url:
                send_tg("🤖 reCAPTCHA detected")
                await asyncio.sleep(10)
                return True
    except:
        pass
    return False

async def run():
    send_tg("🚀 بدء المهمة v5 (مبسطة)...")
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
                "--window-size=1366,768"
            ]
        )

        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0.36"
        )

        await context.add_cookies(MY_COOKIES)
        page = await context.new_page()

        try:
            send_tg("🌐 فتح صفحة اللاب...")
            await page.goto(LAB_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)

            await page.screenshot(path="lab_page.png", full_page=False)
            send_tg("📸 صفحة اللاب مفتوحة", "lab_page.png")
            
            # محاولة النقر
            clicked = await click_start_lab_simple(page)

            if clicked:
                await asyncio.sleep(8)
                await handle_recaptcha(page)
                await asyncio.sleep(10)
                await page.screenshot(path="after_start.png", full_page=False)
                send_tg("📸 بعد الضغط", "after_start.png")
            else:
                send_tg("❌ فشل جميع محاولات النقر")

            await page.screenshot(path="final.png", full_page=False)
            send_tg(f"🏁 انتهت\n🔗 {page.url}", "final.png")

        except Exception as e:
            send_tg(f"❌ خطأ: {str(e)[:400]}")
            await page.screenshot(path="error.png", full_page=False)
            send_tg("📸 لقطة الخطأ", "error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
