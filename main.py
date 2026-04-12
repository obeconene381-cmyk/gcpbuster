import asyncio
import os
import zipfile
import requests
import re
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

async def click_start_lab_button(page, timeout_loop=120, post_click_wait=3):
    pattern = re.compile(r"Start\s*Lab", re.IGNORECASE)

    async def _post_click_stabilize():
        try: 
            await page.wait_for_load_state("domcontentloaded", timeout=2000)
        except: 
            pass
        await asyncio.sleep(post_click_wait)

    for _ in range(timeout_loop):
        targets = [page] + list(page.frames)

        for target in targets:
            try:
                btns = target.get_by_role("button", name=pattern)
                for i in range(await btns.count() - 1, -1, -1):
                    b = btns.nth(i)
                    if await b.is_visible() and await b.is_enabled():
                        await b.scroll_into_view_if_needed(timeout=1000)
                        await b.click(timeout=3000, force=True)
                        await _post_click_stabilize()
                        send_tg("✅ تم النقر على Start Lab")
                        return True
            except:
                continue
        await asyncio.sleep(1)

    return False

async def click_captcha_checkbox(page):
    send_tg("🤛 جاري البحث عن المربع في كل الـ iframes...")
    try:
        await asyncio.sleep(3)
        iframes = await page.locator('iframe').all()
        
        for iframe in iframes:
            frame_content = iframe.content_frame
            checkbox = frame_content.locator('.recaptcha-checkbox-border').first
            
            if await checkbox.count() > 0:
                await checkbox.scroll_into_view_if_needed()
                await checkbox.click(force=True, delay=100)
                send_tg("✅ تم الضغط على المربع بنجاح")
                
                await asyncio.sleep(2)
                img_path = "after_click_instant.png"
                await page.screenshot(path=img_path, full_page=True)
                send_tg("📸 صورة فورية لحالة الكابتشا بعد الضغط:", img_path)
                
                return True
                
        send_tg("❌ لم يتم العثور على المربع في أي iframe.")
        return False
    except Exception as e:
        send_tg(f"❌ خطأ أثناء البحث: {str(e)[:60]}")
        return False

async def handle_buster(page):
    send_tg("🔊 جاري البحث عن نافذة التحدي (Buster)...")
    try:
        challenge_frame = page.frame_locator('iframe[src*="api2/bframe"]').first
        audio_btn = challenge_frame.locator("#recaptcha-audio-button")
        
        await audio_btn.wait_for(state="visible", timeout=10000)
        await audio_btn.click(delay=150)
        send_tg("🔊 تم النقر على زر الصوت")
        await asyncio.sleep(2)
        
        buster_btn = challenge_frame.locator("#solver-button")
        await buster_btn.wait_for(state="visible", timeout=5000)
        
        for attempt in range(3):
            send_tg(f"🎯 Buster محاولة {attempt + 1}/3...")
            try:
                await buster_btn.click(delay=100)
                await asyncio.sleep(15) 
                send_tg(f"✅ Buster محاولة {attempt + 1} اكتملت")
                break 
            except Exception as e:
                send_tg(f"⚠️ Buster محاولة {attempt + 1} فشلت: {str(e)[:60]}")
                await asyncio.sleep(2)
        return True
    except Exception as e:
        send_tg("⚠️ لم يظهر تحدي الصوت أو تم التجاوز التلقائي.")
        return False

async def run_attempt(p, ext_path, proxy_config, proxy_name):
    """دالة فرعية مسؤولة عن محاولة تشغيل اللاب باستخدام بروكسي محدد"""
    send_tg(f"🚀 محاولة بدء المهمة باستخدام البروكسي: {proxy_name}")
    
    browser = await p.chromium.launch(
        headless=True,
        proxy=proxy_config,
        args=[
            f"--disable-extensions-except={ext_path}",
            f"--load-extension={ext_path}",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1280,720",
            "--lang=en-US"
        ]
    )

    context = await browser.new_context(
        viewport={'width': 1280, 'height': 720},
        locale="en-US"
    )

    await context.add_cookies(MY_COOKIES)
    page = await context.new_page()

    try:
        send_tg(f"🌐 فتح صفحة اللاب ({proxy_name})...")
        # مهلة 60 ثانية، إذا لم يستجب البروكسي سيفشل فوراً وننتقل للثاني
        await page.goto(LAB_URL, timeout=60000, wait_until="domcontentloaded")
        await asyncio.sleep(3)

        await page.screenshot(path="lab_page.png", full_page=True)
        send_tg("📸 صفحة اللاب مفتوحة", "lab_page.png")

        clicked = await click_start_lab_button(page, timeout_loop=120, post_click_wait=3)

        if clicked:
            send_tg("⏳ انتظار 5 ثوانٍ...")
            await asyncio.sleep(5)

            await click_captcha_checkbox(page)
            await handle_buster(page)

            await asyncio.sleep(10)
            await page.screenshot(path="after_start.png", full_page=True)
            send_tg("📸 بعد الضغط", "after_start.png")
            
            await page.screenshot(path="final.png", full_page=True)
            send_tg(f"🏁 انتهت المهمة بنجاح عبر ({proxy_name})\n🔗 {page.url}", "final.png")
            return True # نجاح المهمة
            
        else:
            send_tg("❌ فشل في النقر على Start Lab")
            return False # فشل المهمة

    except Exception as e:
        send_tg(f"❌ خطأ في بروكسي {proxy_name}: {str(e)[:150]}")
        try:
            await page.screenshot(path="error.png", full_page=True)
            send_tg("📸 لقطة الخطأ", "error.png")
        except:
            pass
        return False # فشل المهمة (البروكسي غالباً لا يستجيب)
    finally:
        await browser.close()

async def run():
    ext_path = await get_ext()
    
    # قائمة البروكسيات بالترتيب الذي تريد تجربته
    proxies = [
        {
            "name": "AstroProxy (SOCKS5)",
            "config": {
                "server": "socks5://node-de-91.astroproxy.com:10054",
                "username": "ShinoharitoshiJB4",
                "password": "bfdb58IN2"
            }
        },
        {
            "name": "البروكسي الاحتياطي (HTTP)",
            "config": {
                "server": "http://92.119.128.15:9996",
                "username": "user376353",
                "password": "y3ld6w"
            }
        }
    ]

    async with async_playwright() as p:
        for proxy in proxies:
            # نجرب تشغيل المهمة بالبروكسي الحالي
            success = await run_attempt(p, ext_path, proxy["config"], proxy["name"])
            
            # إذا نجحت المهمة، نخرج من الحلقة (لا داعي لتجربة البروكسي الثاني)
            if success:
                break
            else:
                send_tg(f"🔄 جاري الانتقال للبروكسي التالي...")
        else:
            # تتنفذ هذه الأسطر إذا فشلت جميع البروكسيات في القائمة
            send_tg("❌🚨 فشلت جميع البروكسيات المتاحة. يرجى التحقق من اشتراكاتك أو تجديد الـ IPs.")

if __name__ == "__main__":
    asyncio.run(run())
