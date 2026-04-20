import telebot
import time
import os
from threading import Thread
from flask import Flask
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs, unquote

# Tera Telegram Bot Token
BOT_TOKEN = "8545950878:AAFp2j-S331ltnD_jHmy00hi1F67YUYF6RM"
bot = telebot.TeleBot(BOT_TOKEN)

# --- FAKE WEBSITE FOR RENDER (FREE TIER) ---
app = Flask('')
@app.route('/')
def home():
    return "The Mods King Bot is Alive & Running!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
# -------------------------------------------

def headless_bypasser(target_url):
    print(f"\n[*] Processing New Link: {target_url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled', '--disable-dev-shm-usage'])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        try:
            page.goto(target_url, timeout=60000)

            for step in range(4):
                page.wait_for_timeout(5000)
                current_url = page.url
                print(f"[-] Step {step+1} Current URL: {current_url}")

                if not any(x in current_url for x in ["whatsagrouplink", "newsuchnaonline", "thewiar", "go.just2earn", "go.yorurl", "caslinks", "mypdftools"]):
                    break

                # Blogs
                if any(x in current_url for x in ["whatsagrouplink", "newsuchnaonline", "thewiar"]):
                    forms = page.locator("form")
                    if forms.count() > 0:
                        forms.first.evaluate("form => form.submit()")
                        page.wait_for_load_state("domcontentloaded", timeout=30000)
                        continue
                        
                    links = page.locator("a")
                    clicked = False
                    for i in range(links.count()):
                        href = links.nth(i).get_attribute("href")
                        if href and ("off.php" in href or "go." in href or "link=" in href):
                            links.nth(i).evaluate("node => node.click()")
                            page.wait_for_load_state("domcontentloaded", timeout=30000)
                            clicked = True
                            break
                    if clicked: continue

                # Gateways
                elif any(x in current_url for x in ["go.just2earn", "go.yorurl", "caslinks", "mypdftools"]):
                    page.wait_for_timeout(10000)
                    form = page.locator("#go-link")
                    if form.count() > 0:
                        form.evaluate("form => form.submit()")
                        page.wait_for_load_state("networkidle", timeout=30000)
                        page.wait_for_timeout(3000)
                        break
                    else:
                        return "[-] Error: Gateway form nahi mila."

            final_url = page.url
            if "url=" in final_url.lower():
                qs = parse_qs(urlparse(final_url).query)
                if 'url' in qs:
                    final_url = unquote(qs['url'][0])

            return final_url
        except Exception as e:
            return f"[-] Runtime Error: {str(e)}"
        finally:
            browser.close()

@bot.message_handler(commands=['start', 'help'])
def start_msg(message):
    bot.reply_to(message, "👑 **The Mods King Headless Bot Live!** 👑\n\nYorURL, Caslinks, ya Just2Earn ki link bhej.", parse_mode="Markdown")

@bot.message_handler(func=lambda msg: True)
def process_link(message):
    url = message.text.strip()
    if not url.startswith("http"):
        bot.reply_to(message, "⚠️ Bhai valid link bhej (http:// ya https://).")
        return

    msg_id = bot.reply_to(message, "⏳ *Intercepting Link...*\n_Bypassing Cloudflare..._", parse_mode="Markdown").message_id
    start_time = time.time()
    result = headless_bypasser(url)
    elapsed = int(time.time() - start_time)

    if result and result.startswith("http") and not any(x in result for x in ["whatsagrouplink", "newsuchnaonline", "thewiar", "go.just2earn", "go.yorurl"]):
        text = f"✅ **Bypass Successful!**\n\n🔓 `{result}`\n\n⏱ **Time:** {elapsed}s\n👑 _Powered By The Mods King_"
    else:
        text = f"❌ **Bypass Failed!**\n\n**Details:** {result}\n\n👑 _Powered By The Mods King_"

    bot.edit_message_text(text, chat_id=message.chat.id, message_id=msg_id, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == "__main__":
    # Start the fake web server in background
    server = Thread(target=run_server)
    server.start()
    
    print("─"*50)
    print(" 🔥 THE MODS KING BOT IS RUNNING (FREE RENDER MODE) 🔥")
    print("─"*50)
    bot.infinity_polling()
