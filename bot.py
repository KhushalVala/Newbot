import telebot, time, os
from threading import Thread
from flask import Flask
from playwright.sync_api import sync_playwright

BOT_TOKEN = "8545950878:AAFp2j-S331ltnD_jHmy00hi1F67YUYF6RM"
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask('')
@app.route('/')
def home(): return "The Mods King Bot is Online!"
def run_server(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

def headless_bypasser(target_url):
    with sync_playwright() as p:
        # Extra stealth flags to hide automation
        browser = p.chromium.launch(headless=True, args=[
            '--no-sandbox', 
            '--disable-setuid-sandbox', 
            '--disable-blink-features=AutomationControlled'
        ])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()

        try:
            # 1. Disable image loading for speed
            page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())
            
            print(f"[*] Navigating to: {target_url}")
            page.goto(target_url, wait_until="load", timeout=60000)

            for step in range(5):
                page.wait_for_timeout(3000)
                curr_url = page.url
                
                # Check if we are out of the link system
                if not any(x in curr_url for x in ["whatsagrouplink", "newsuchnaonline", "thewiar", "just2earn", "yorurl", "caslinks"]):
                    break

                # BYPASS CLOUDFLARE TICK (If visible)
                if page.locator("iframe[title*='Cloudflare']").count() > 0:
                    print("[!] Cloudflare Detected! Human simulation active...")
                    page.mouse.move(100, 100) # Fake mouse movement
                    page.wait_for_timeout(5000)

                # FIND AND CLICK BUTTONS (Using coordinates to mimic human)
                btn = page.locator("button:visible, input[type='submit']:visible, a.btn:visible").first
                if btn.count() > 0:
                    print(f"[*] Clicking button on: {curr_url}")
                    btn.click(delay=150) # Insaan ki tarah thoda delay karke click
                    page.wait_for_load_state("domcontentloaded")
                    continue

                # ADLINKFLY / JUST2EARN TIMER
                if "go-link" in page.content() or "btn-main" in page.content():
                    print("[*] Timer Page Detected. Waiting 10s...")
                    page.wait_for_timeout(10000)
                    # Submit direct via JS to bypass broken UI buttons
                    page.evaluate("() => { document.forms[0].submit(); }")
                    page.wait_for_load_state("networkidle")
                    break

            return page.url
        except Exception as e:
            return f"Bypass Failed: {str(e)}"
        finally:
            browser.close()

@bot.message_handler(func=lambda m: True)
def process(message):
    msg = bot.reply_to(message, "⚡ **The Mods King: CRACKING ENGINE START...**")
    res = headless_bypasser(message.text.strip())
    bot.edit_message_text(f"✅ **Result:**\n`{res}`", message.chat.id, msg.message_id, parse_mode="Markdown")

if __name__ == "__main__":
    Thread(target=run_server).start()
    bot.infinity_polling()
