import time
import re
import os
import threading
from urllib.parse import urlparse, parse_qs, unquote
import telebot
from flask import Flask
from curl_cffi import requests # 👈 Asali Chrome jaisa bypass engine

# --- BOT CONFIG ---
BOT_TOKEN = "8545950878:AAFp2j-S331ltnD_jHmy00hi1F67YUYF6RM"
bot = telebot.TeleBot(BOT_TOKEN)

# --- RENDER KEEP-ALIVE SERVER ---
app = Flask('')
@app.route('/')
def home(): return "TMK Auto-Bypass Bot is Online!"
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
# ⚡ AUTO BYPASS ENGINE (CURL_CFFI)
# ==========================================================
def run_assassin_bypass(short_url, chat_id, msg_id):
    def update_status(text):
        try: bot.edit_message_text(f"⚡ **Assassin Engine v23**\n`{text}`", chat_id, msg_id, parse_mode="Markdown")
        except: pass

    try:
        clean_url = short_url.split('?')[0].strip('/')
        link_id = clean_url.split('/')[-1]
        if len(link_id) < 4 or link_id.lower() in ["api", "step2", "started", "resolve", "get", "v3"]:
            return "[-] Error: Invalid Link Format!"
    except: return "[-] Error: Cannot extract ID!"

    # Create a Chrome-impersonating session
    session = requests.Session(impersonate="chrome120")
    
    try:
        # Phase 0
        update_status("[*] Piercing Cloudflare Shield...")
        res = session.get(f"https://go.urlking.site/{link_id}")
        if res.status_code in [403, 503]:
            return "[-] Error: Heavy Cloudflare Block Detected."
        time.sleep(1)

        # Phase 1
        update_status("[*] Spoofing Traffic Source...")
        blog_url = f"https://mypdftools.pages.dev/blog/#id={link_id}"
        session.get(blog_url, headers={"Referer": "https://www.google.com/"})
        time.sleep(1)

        # Phase 2
        update_status("[*] Activating Backend Triggers...")
        session.get(f"https://go.urlking.site/api/step1/{link_id}", headers={"Referer": f"https://go.urlking.site/{link_id}"})
        session.get(f"https://go.urlking.site/api/step2/{link_id}", headers={"Referer": f"https://go.urlking.site/{link_id}"})
        time.sleep(1)

        # Phase 3
        update_status("[*] Passing Secure Gateway...")
        session.get(f"https://get.urlking.site/get/?id={link_id}", headers={"Referer": "https://mypdftools.pages.dev/"})
        time.sleep(1.5)

        # Phase 4
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
                session.get(f"https://go.urlking.site/{link_id}")
                time.sleep(2)
            else: break

        # Phase 5
        if final_raw_link:
            update_status("[*] Cleaning Decrypted Link...")
            clean_link = final_raw_link
            if "go.yorurl.com" in clean_link:
                clean_link = bypass_yorurl_short(clean_link, session)
            return safe_extract(clean_link)
        else:
            return "[-] Error: Bypass Failed."

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
    print("🔥 THE MODS KING BOT IS LIVE (CURL_CFFI EDITION) 🔥")
    bot.infinity_polling()
