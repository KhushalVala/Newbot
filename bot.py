import telebot
import time
import re
import os
import cloudscraper
from threading import Thread
from flask import Flask
from urllib.parse import urlparse, parse_qs, unquote

# --- BOT CONFIG ---
BOT_TOKEN = "8545950878:AAFp2j-S331ltnD_jHmy00hi1F67YUYF6RM"
bot = telebot.TeleBot(BOT_TOKEN)

# --- RENDER KEEP-ALIVE SERVER ---
app = Flask('')
@app.route('/')
def home(): return "The Mods King Assassin Bot is Online!"
def run_server(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# ==========================================================
# 💎 TERA ORIGINAL LOGIC (NO CHANGES)
# ==========================================================

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

def bypass_yorurl_short(short_url, scraper):
    match = re.search(r'go\.yorurl\.com/([a-zA-Z0-9]+)', short_url)
    if not match: return short_url
    yor_id = match.group(1)
    scraper.cookies.set(f'start_{yor_id}', str(int(time.time())), domain='go.yorurl.com')
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://how2guidess.com/",
        "Upgrade-Insecure-Requests": "1"
    }
    try:
        res = scraper.get(short_url, headers=headers)
        meta = re.search(r'content=["\']\d+;url=(.*?)["\']', res.text, re.IGNORECASE)
        if meta: return meta.group(1)
        script_redir = re.search(r'window\.location\.href\s*=\s*["\'](.*?)["\']', res.text)
        if script_redir: return script_redir.group(1)
    except: pass
    return short_url

# ==========================================================
# ⚡ MAIN BYPASS FUNCTION (INTEGRATED)
# ==========================================================

def run_assassin_bypass(short_url, chat_id, msg_id):
    def update_status(text):
        try: bot.edit_message_text(f"⚡ **Assassin Engine**\n`{text}`", chat_id, msg_id, parse_mode="Markdown")
        except: pass

    match = re.search(r'(gx\d+)', short_url)
    if not match: return "[-] Error: URL mein ID (gx...) nahi mili!"
    
    link_id = match.group(1)
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'android', 'desktop': False})
    user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"

    try:
        # Phase 1
        update_status("Phase 1: Injecting Start Signal...")
        start_headers = {"User-Agent": user_agent, "Accept": "*/*", "Content-Type": "application/json", "Origin": "https://mypdftools.pages.dev", "Referer": "https://mypdftools.pages.dev/"}
        scraper.post("https://go.urlking.site/api/started", json={"id": link_id}, headers=start_headers)
        time.sleep(0.5)

        # Phase 2
        update_status("Phase 2: Secure Gateway...")
        gateway_headers = {"User-Agent": user_agent, "Referer": "https://mypdftools.pages.dev/", "Upgrade-Insecure-Requests": "1"}
        scraper.get(f"https://get.urlking.site/get/?id={link_id}", headers=gateway_headers)
        time.sleep(1)

        # Phase 3
        update_status("Phase 3: Handling Timer Battle...")
        api_headers = {"User-Agent": user_agent, "Accept": "*/*", "Origin": "https://get.urlking.site", "Referer": "https://get.urlking.site/"}
        resolve_url = f"https://go.urlking.site/api/v3/resolve?id={link_id}&_t={int(time.time() * 1000)}"
        
        final_raw_link = None
        for attempt in range(15):
            response = scraper.get(resolve_url, headers=api_headers)
            try: data = response.json()
            except: return "[-] Server Error: JSON nahi mila (IP Blocked?)"
            
            if data.get("url"):
                final_raw_link = data['url']
                break
            elif data.get("error") == "wait_timer":
                wait = data.get("remaining", 5)
                update_status(f"Timer: Wait {wait}s more...")
                time.sleep(wait)
            elif data.get("error") == "start_required":
                scraper.post("https://go.urlking.site/api/started", json={"id": link_id}, headers=start_headers)
                time.sleep(2)
            else: break

        # Phase 4
        if final_raw_link:
            update_status("Phase 4: Final Polishing...")
            clean_link = final_raw_link
            if "go.yorurl.com" in clean_link:
                clean_link = bypass_yorurl_short(clean_link, scraper)
            return safe_extract(clean_link)
        else:
            return "[-] Error: Process Timed Out."

    except Exception as e:
        return f"[-] Fatal Error: {str(e)}"

# ==========================================================
# 🤖 BOT HANDLERS
# ==========================================================

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👑 **The Mods King Assassin Bot Live!**\nSend me go.urlking.site links.")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    url = message.text.strip()
    if "go.urlking.site" not in url:
        bot.reply_to(message, "⚠️ Bhai sirf go.urlking.site ki links bhej.")
        return

    init_msg = bot.reply_to(message, "⚡ **Assassin Engine: INJECTING...**")
    final_result = run_assassin_bypass(url, message.chat.id, init_msg.message_id)
    
    bot.edit_message_text(f"✅ **Destination Found!**\n\n🔗 `{final_result}`\n\n👑 _The Mods King Legacy_", message.chat.id, init_msg.message_id, parse_mode="Markdown")

if __name__ == "__main__":
    Thread(target=run_server).start()
    bot.infinity_polling()
