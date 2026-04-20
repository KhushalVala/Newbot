import telebot, time, os
from threading import Thread
from flask import Flask
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs, unquote

# --- CONFIGURATION ---
BOT_TOKEN = "8545950878:AAFp2j-S331ltnD_jHmy00hi1F67YUYF6RM"
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask('')

@app.route('/')
def home(): 
    return "The Mods King Bot is Alive!"

def run_server(): 
    # Render/Heroku ke liye port 10000 standard hai
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

def log_status(chat_id, msg_id, status_text):
    try:
        bot.edit_message_text(
            f"⚡ **The Mods King Engine**\n\nSTATUS: `{status_text}`", 
            chat_id, msg_id, parse_mode="Markdown"
        )
    except Exception as e:
        # Agar message edit nahi ho raha to ignore kar do
        pass

def bypasser_logic(url, chat_id, msg_id):
    try:
        with sync_playwright() as p:
            # Browser Launch (Headless)
            browser = p.chromium.launch(headless=True, args=[
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ])

            # --- IMPORTANT UPDATE (BASED ON LOGS) ---
            # Humne Mobile View set kiya hai kyunki tumhare logs mein tha
            # User-Agent: Android 10, Chrome 137
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
                viewport={'width': 393, 'height': 886}, # Mobile Screen Size
                locale='en-US'
            )
            
            page = context.new_page()
            
            log_status(chat_id, msg_id, "🚀 Connecting to Source...")
            
            # Page Load
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Logic Loop
            for step in range(1, 7):
                current_url = page.url
                log_status(chat_id, msg_id, f"🔄 Processing Step {step}...")

                # 1. Cloudflare Detection (Logs mein jsd/oneshot dikh raha tha)
                if "Checking your browser" in page.content() or "cf-challenge" in current_url:
                    log_status(chat_id, msg_id, "🛡️ Solving Cloudflare...")
                    page.wait_for_timeout(8000) # Wait for JS challenge
                
                # 2. Blog Logic (NewsSuchna, TheWiar, WhatsAGroup)
                # Logs mein in sites pe 'off.php' se redirect hota hai
                if any(x in current_url for x in ["newsuchnaonline", "thewiar", "whatsagrouplink"]):
                    log_status(chat_id, msg_id, "📝 Blog Detected. Waiting...")
                    
                    # Wait for redirection (off.php -> samsung-galaxy-s24...)
                    page.wait_for_timeout(5000)
                    
                    # Agar page par "Get Link" ya form submit button ho to click karo
                    try:
                        # Try clicking the most likely button
                        if page.locator("input[type='submit']").count() > 0:
                            page.locator("input[type='submit']").first.click(timeout=2000)
                        elif page.locator("button").count() > 0:
                            page.locator("button").first.click(timeout=2000)
                    except:
                        pass # Ignore agar button nahi mila
                    
                    # Wait for network to settle after click
                    page.wait_for_load_state("networkidle", timeout=5000)
                    continue

                # 3. Gateway Logic (Just2Earn, YorURL)
                if any(x in current_url for x in ["just2earn", "yorurl", "caslinks"]):
                    log_status(chat_id, msg_id, "⏳ Gateway Timer...")
                    # Wait 10 seconds standard
                    page.wait_for_timeout(10000)
                    
                    # Trigger final redirection logic
                    try:
                        page.evaluate("() => { if(typeof go === 'function') go(); else document.forms[0].submit(); }")
                    except:
                        pass
                    
                    page.wait_for_load_state("networkidle")
                    break
            
            # Final Link Extraction
            final_link = page.url
            
            # Check if link is in query parameters (URL redirection)
            if "url=" in final_link:
                parsed = urlparse(final_link)
                params = parse_qs(parsed.query)
                if 'url' in params:
                    final_link = unquote(params['url'][0])
            
            return final_link

    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        try:
            browser.close()
        except:
            pass

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text.strip()
    if not url.startswith("http"):
        return bot.reply_to(message, "Bhai, valid link daal! http:// ya https:// ke sath.")
    
    # Initial Response
    initial_msg = bot.reply_to(message, "⚡ **The Mods King Engine: STARTING...**")
    
    # Run Bypasser
    final_res = bypasser_logic(url, message.chat.id, initial_msg.message_id)
    
    # Send Final Result
    bot.edit_message_text(
        f"✅ **Bypassed Successfully!**\n\n🔓 `{final_res}`\n\n👑 _The Mods King Legacy_", 
        message.chat.id, initial_msg.message_id, parse_mode="Markdown"
    )

if __name__ == "__main__":
    # Server ko background mein chalao
    Thread(target=run_server).start()
    print("Bot Started Polling...")
    bot.infinity_polling()
