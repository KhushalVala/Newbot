import telebot
import time
import os
from threading import Thread
from flask import Flask
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs, unquote

BOT_TOKEN = "8545950878:AAFp2j-S331ltnD_jHmy00hi1F67YUYF6RM"
bot = telebot.TeleBot(BOT_TOKEN)

# --- FAKE WEBSITE FOR RENDER ---
app = Flask('')
@app.route('/')
def home(): return "The Mods King Bot is Online!"
def run_server(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

def headless_bypasser(target_url):
    with sync_playwright() as p:
        # Browser launch with optimization
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()

        # BLOCK ADS & IMAGES (Speed badhane ke liye)
        page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,otf}", lambda route: route.abort())

        try:
            # 1. Seedha target link par jao
            page.goto(target_url, wait_until="domcontentloaded", timeout=30000)

            for _ in range(5): # Max 5 jumps
                curr_url = page.url
                print(f"[*] Current: {curr_url}")

                # Check if reached destination
                if not any(x in curr_url for x in ["whatsagrouplink", "newsuchnaonline", "thewiar", "just2earn", "yorurl", "caslinks"]):
                    break

                # AGAR CLOUDFLARE HAI TOH WAIT KARO (Sirf jab zaroorat ho)
                if "Checking your browser" in page.content():
                    page.wait_for_timeout(4000)

                # FAST FORM SUBMISSION
                form = page.locator("form")
                if form.count() > 0:
                    form.first.evaluate("form => form.submit()")
                    page.wait_for_load_state("domcontentloaded")
                    continue

                # FAST LINK CLICKING
                jump_link = page.locator("a:has-text('Click here'), a:has-text('Continue'), a[href*='off.php'], a[href*='link=']")
                if jump_link.count() > 0:
                    jump_link.first.click()
                    page.wait_for_load_state("domcontentloaded")
                    continue
                
                # ADLINKFLY TIMER BYPASS (YorURL/Just2Earn)
                if "go-link" in page.content():
                    # Timer ka wait nahi, sidha button click try karo
                    page.wait_for_timeout(8000) # Minimum server time
                    page.evaluate("() => { if(typeof(go) !== 'undefined') { go(); } else { document.getElementById('go-link').submit(); } }")
                    page.wait_for_load_state("networkidle")
                    break

            # Final URL Clean
            final_url = page.url
            if "url=" in final_url.lower():
                final_url = unquote(parse_qs(urlparse(final_url).query)['url'][0])
            
            return final_url
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            browser.close()

@bot.message_handler(func=lambda m: True)
def process(message):
    msg = bot.reply_to(message, "⚡ **The Mods King: Fast Bypassing...**")
    res = headless_bypasser(message.text.strip())
    bot.edit_message_text(f"✅ **Bypassed:**\n`{res}`", message.chat.id, msg.message_id, parse_mode="Markdown")

if __name__ == "__main__":
    Thread(target=run_server).start()
    bot.infinity_polling()
