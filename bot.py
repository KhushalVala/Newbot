import time
import re
import os
import threading
from urllib.parse import urlparse, parse_qs, unquote
import telebot
from flask import Flask
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# --- BOT CONFIG ---
BOT_TOKEN = "8545950878:AAHP0iHL-wtEa1dC_P9mN3ghKAHdhLivRiY"
bot = telebot.TeleBot(BOT_TOKEN)

# --- RENDER KEEP-ALIVE SERVER ---
app = Flask('')
@app.route('/')
def home(): return "TMK Master Engine is Online!"
def run_server(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

def auto_delete(chat_id, user_msg_id, bot_msg_id):
    time.sleep(60)
    try:
        bot.delete_message(chat_id, user_msg_id)
        bot.delete_message(chat_id, bot_msg_id)
    except: pass

def safe_extract(nested_url):
    current_url = nested_url
    try:
        parsed = urlparse(current_url)
        params = parse_qs(parsed.query)
        if 'url' in params and params['url'][0].startswith('http'):
            extracted = unquote(params['url'][0])
            if "token" not in current_url.lower() and "verify" not in current_url.lower():
                current_url = extracted
    except: pass
    return current_url

# ==========================================================
# 🚀 REAL BROWSER ENGINE (PLAYWRIGHT)
# ==========================================================
def run_master_bypass(short_url, chat_id, msg_id):
    def update_status(text):
        try: bot.edit_message_text(f"⚡ **Master Engine v26**\n`{text}`", chat_id, msg_id, parse_mode="Markdown")
        except: pass

    try:
        link_id = short_url.split('?')[0].strip('/').split('/')[-1]
        if len(link_id) < 4: return "[-] Error: Invalid Link ID"
    except: return "[-] Error: Format Error"

    update_status("[*] Launching Invisible Chrome Browser...")
    
    try:
        with sync_playwright() as p:
            # Launch Chrome Headless (No UI)
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Apply Stealth to bypass Cloudflare
            stealth_sync(page)

            # PHASE 1: Beating Cloudflare
            update_status("[*] Solving Cloudflare JS Challenge...")
            page.goto(f"https://go.urlking.site/{link_id}")
            
            try:
                # Wait until the title is NO LONGER "Just a moment..." (CF Challenge passed)
                page.wait_for_function('document.title !== "Just a moment..."', timeout=15000)
            except:
                return "[-] Error: Cloudflare Challenge is too strong today!"
            
            time.sleep(2)

            # PHASE 2: Triggering APIs internally via Browser Console
            update_status("[*] Injecting Backend API Triggers...")
            # Parde ke peeche Chrome ke andar hi requests fire kar rahe hain (No CORS issues)
            trigger_js = f"""
            async () => {{
                await fetch('https://go.urlking.site/api/step1/{link_id}');
                await fetch('https://go.urlking.site/api/step2/{link_id}');
                return true;
            }}
            """
            page.evaluate(trigger_js)
            time.sleep(2)

            # PHASE 3: Loading Gateway
            update_status("[*] Loading Secure Gateway...")
            page.goto(f"https://get.urlking.site/get/?id={link_id}")
            time.sleep(2)

            # PHASE 4: Cracking the Timer
            update_status("[*] Cracking Server Timer...")
            final_raw_link = None
            
            for attempt in range(15):
                # Browser ke andar hi Resolve API ko hit kar rahe hain
                resolve_js = f"""
                async () => {{
                    try {{
                        let res = await fetch('https://go.urlking.site/api/v3/resolve?id={link_id}&_t=' + Date.now());
                        return await res.json();
                    }} catch(e) {{ return {{"error": "network"}}; }}
                }}
                """
                data = page.evaluate(resolve_js)
                
                if data.get('url'):
                    final_raw_link = data['url']
                    break
                elif data.get('error') == 'wait_timer':
                    wait = data.get('remaining', 5)
                    update_status(f"[*] Timer: Wait {wait}s...")
                    time.sleep(wait)
                else:
                    time.sleep(2)

            # Cleanup and Extract
            browser.close()

            if final_raw_link:
                update_status("[*] Cleaning Decrypted Link...")
                clean_link = final_raw_link
                # Simple YorUrl resolve if needed
                if "go.yorurl.com" in clean_link:
                    import requests
                    try:
                        r = requests.get(clean_link, headers={"Referer": "https://how2guidess.com/"})
                        m = re.search(r'content=["\']\d+;url=(.*?)["\']', r.text, re.IGNORECASE)
                        if m: clean_link = m.group(1)
                    except: pass
                
                return safe_extract(clean_link)
            else:
                return "[-] Error: Link could not be decrypted."

    except Exception as e:
        return f"[-] Fatal Engine Error: {str(e)}"

# ==========================================================
# 🤖 BOT HANDLERS
# ==========================================================
@bot.message_handler(commands=['start', 'help'])
def start_cmd(message):
    bot.reply_to(message, "👑 **The Mods King Master Engine Live!**\n\nSend me `urlking` links.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    url = message.text.strip()
    if "urlking" not in url:
        return bot.reply_to(message, "⚠️ Bhai sirf URLKing ki links bhej.")

    init_msg = bot.reply_to(message, "⚡ **Master Engine: STARTING...**")
    
    final_result = run_master_bypass(url, message.chat.id, init_msg.message_id)
    
    if final_result.startswith("http"):
        text = f"✅ **Destination Unlocked!**\n\n🔗 `{final_result}`\n\n👑 _The Mods King Legacy_\n🗑 _Chat auto-clears in 60s_"
    else:
        text = f"❌ **Failed:**\n`{final_result}`\n\n👑 _The Mods King Legacy_"

    bot.edit_message_text(text, chat_id=message.chat.id, message_id=init_msg.message_id, parse_mode="Markdown", disable_web_page_preview=True)
    threading.Thread(target=auto_delete, args=(message.chat.id, message.message_id, init_msg.message_id)).start()

if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    print("🔥 THE MODS KING BOT IS LIVE (PLAYWRIGHT ENGINE) 🔥")
    bot.infinity_polling()
