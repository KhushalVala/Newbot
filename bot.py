import time
import re
import os
import threading
from urllib.parse import urlparse, parse_qs, unquote
import telebot
from flask import Flask
from curl_cffi import requests # Asali Chrome engine

# --- BOT CONFIG ---
BOT_TOKEN = "8545950878:AAHP0iHL-wtEa1dC_P9mN3ghKAHdhLivRiY"
bot = telebot.TeleBot(BOT_TOKEN)

# --- RENDER KEEP-ALIVE SERVER ---
app = Flask('')
@app.route('/')
def home(): return "TMK Auto-Bypass Bot v25 is Online!"
def run_server(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# ==========================================================
# 🧹 AUTO-DELETE ENGINE
# ==========================================================
def auto_delete(chat_id, user_msg_id, bot_msg_id):
    time.sleep(60)
    try:
        bot.delete_message(chat_id, user_msg_id)
        bot.delete_message(chat_id, bot_msg_id)
    except: pass

# ==========================================================
# 💎 EXTRACTION LOGIC
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

def bypass_yorurl_short(short_url, session):
    match = re.search(r'go\.yorurl\.com/([a-zA-Z0-9]+)', short_url)
    if not match: return short_url
    yor_id = match.group(1)
    session.cookies.set(f'start_{yor_id}', str(int(time.time())), domain='go.yorurl.com')
    try:
        res = session.get(short_url, headers={"Referer": "https://how2guidess.com/"})
        meta = re.search(r'content=["\']\d+;url=(.*?)["\']', res.text, re.IGNORECASE)
        if meta: return meta.group(1)
        script_redir = re.search(r'window\.location\.href\s*=\s*["\'](.*?)["\']', res.text)
        if script_redir: return script_redir.group(1)
    except: pass
    return short_url

# ==========================================================
# ⚡ AUTO BYPASS ENGINE (CURL_CFFI V25)
# ==========================================================
def run_assassin_bypass(short_url, chat_id, msg_id):
    def update_status(text):
        try: bot.edit_message_text(f"⚡ **Assassin Engine v25**\n`{text}`", chat_id, msg_id, parse_mode="Markdown")
        except: pass

    try:
        clean_url = short_url.split('?')[0].strip('/')
        link_id = clean_url.split('/')[-1]
        if len(link_id) < 4 or link_id.lower() in ["api", "step2", "started", "resolve", "get", "v3"]:
            return "[-] Error: Invalid Link Format!"
    except: return "[-] Error: Cannot extract ID!"

    # Impersonate a real Windows Chrome browser
    session = requests.Session(impersonate="chrome120")
    
    try:
        # Phase 0: The YouTube Spoof Trick
        update_status("[*] Masking Bot as YouTube Traffic...")
        spoof_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.youtube.com/", # 👈 Ye Cloudflare ko bewakoof banayega
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site"
        }
        
        res = session.get(f"https://go.urlking.site/{link_id}", headers=spoof_headers)
        
        # Check if Cloudflare caught us
        if "just a moment" in res.text.lower() or "challenge-platform" in res.text.lower():
            return "[-] Error: Cloudflare JS Challenge activated! Bot blocked."
        
        time.sleep(1)

        # Phase 1: Simulate Flow
        update_status("[*] Loading Ghost Session...")
        blog_url = f"https://mypdftools.pages.dev/blog/#id={link_id}"
        session.get(blog_url, headers={"Referer": "https://www.google.com/"})
        time.sleep(1)

        # Phase 2: Gateway
        update_status("[*] Passing Secure Gateway...")
        session.get(f"https://get.urlking.site/get/?id={link_id}", headers={"Referer": "https://mypdftools.pages.dev/"})
        time.sleep(1.5)

        # Phase 3: The Resolver
        update_status("[*] Cracking Server Timer...")
        api_headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://get.urlking.site",
            "Referer": "https://get.urlking.site/",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        final_raw_link = None
        for attempt in range(15):
            resolve_url = f"https://go.urlking.site/api/v3/resolve?id={link_id}&_t={int(time.time() * 1000)}"
            response = session.get(resolve_url, headers=api_headers)
            
            try: data = response.json()
            except: 
                time.sleep(1)
                continue
            
            if data.get("url"):
                final_raw_link = data['url']
                break
            elif data.get("error") == "wait_timer":
                wait = data.get("remaining", 5)
                update_status(f"[*] Timer: {wait}s remaining...")
                time.sleep(wait)
            elif data.get("error") == "start_required":
                # Re-hit session if dropped
                update_status("[!] Timer Dropped. Re-injecting...")
                session.get(f"https://go.urlking.site/{link_id}", headers=spoof_headers)
                time.sleep(2)
            else: 
                return f"[-] Debug: Unexpected JSON - {data}"

        # Phase 4: Extraction
        if final_raw_link:
            update_status("[*] Cleaning Decrypted Link...")
            clean_link = final_raw_link
            if "go.yorurl.com" in clean_link:
                clean_link = bypass_yorurl_short(clean_link, session)
            return safe_extract(clean_link)
        else:
            return "[-] Error: Bypass Failed. Could not extract link."

    except Exception as e:
        return f"[-] Fatal Error: {str(e)}"

# ==========================================================
# 🤖 BOT HANDLERS
# ==========================================================
@bot.message_handler(commands=['start', 'help'])
def start_cmd(message):
    bot.reply_to(message, "👑 **The Mods King Auto-Bypass Bot Live!**\n\nSend me `urlking` links to bypass.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    url = message.text.strip()
    if "urlking" not in url:
        return bot.reply_to(message, "⚠️ Bhai sirf URLKing ki links bhej.")

    init_msg = bot.reply_to(message, "⚡ **Assassin Engine: STARTING...**")
    
    final_result = run_assassin_bypass(url, message.chat.id, init_msg.message_id)
    
    if final_result.startswith("http"):
        text = f"✅ **Destination Unlocked!**\n\n🔗 `{final_result}`\n\n👑 _The Mods King Legacy_\n🗑 _Chat auto-clears in 60s_"
    else:
        text = f"❌ **Failed:**\n`{final_result}`\n\n👑 _The Mods King Legacy_"

    bot.edit_message_text(text, chat_id=message.chat.id, message_id=init_msg.message_id, parse_mode="Markdown", disable_web_page_preview=True)

    # Start Auto-Delete
    threading.Thread(target=auto_delete, args=(message.chat.id, message.message_id, init_msg.message_id)).start()

if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    print("🔥 THE MODS KING BOT IS LIVE (V25 YOUTUBE TRICK) 🔥")
    bot.infinity_polling()
