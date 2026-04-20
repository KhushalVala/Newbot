import telebot
import time
import re
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs, unquote

# Tera Telegram Bot Token
BOT_TOKEN = "8545950878:AAFp2j-S331ltnD_jHmy00hi1F67YUYF6RM"
bot = telebot.TeleBot(BOT_TOKEN)

def headless_bypasser(target_url):
    print(f"\n[*] Processing New Link: {target_url}")
    
    with sync_playwright() as p:
        # Memory fix flag added (--disable-dev-shm-usage)
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled', '--disable-dev-shm-usage'])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        try:
            # Page load karna start
            page.goto(target_url, timeout=60000)

            # Max 4 steps tak redirects/blogs follow karega
            for step in range(4):
                # Cloudflare check clear hone ke liye extra wait
                page.wait_for_timeout(5000)
                current_url = page.url
                
                print(f"[-] Step {step+1} Current URL: {current_url}")

                # Agar asali destination par pahunch gaye (Gateway se aage)
                if not any(x in current_url for x in ["whatsagrouplink", "newsuchnaonline", "thewiar", "go.just2earn", "go.yorurl", "caslinks", "mypdftools"]):
                    break

                # ==========================================
                # PHASE 1: Safelink Blogs (newsuchnaonline, whatsagrouplink, thewiar)
                # ==========================================
                if any(x in current_url for x in ["whatsagrouplink", "newsuchnaonline", "thewiar"]):
                    print("[*] Detected Safelink Blog. Searching for forms/links...")
                    
                    # Agar koi form submit karna hai
                    forms = page.locator("form")
                    if forms.count() > 0:
                        print("[*] Submitting Blog Form...")
                        forms.first.evaluate("form => form.submit()")
                        page.wait_for_load_state("domcontentloaded", timeout=30000)
                        continue
                        
                    # Agar off.php ya sidha gateway link par click karna hai
                    links = page.locator("a")
                    clicked = False
                    for i in range(links.count()):
                        href = links.nth(i).get_attribute("href")
                        if href and ("off.php" in href or "go." in href or "link=" in href):
                            print("[*] Clicking Jump Link...")
                            links.nth(i).evaluate("node => node.click()")
                            page.wait_for_load_state("domcontentloaded", timeout=30000)
                            clicked = True
                            break
                    if clicked: continue

                # ==========================================
                # PHASE 2: Gateway (go.just2earn / go.yorurl / mypdftools)
                # ==========================================
                elif any(x in current_url for x in ["go.just2earn", "go.yorurl", "caslinks", "mypdftools"]):
                    print("[*] Detected Adlinkfly Gateway. Syncing Timer...")
                    
                    # Backend timer ke liye 9-10 seconds ka wait zaroori hai
                    page.wait_for_timeout(10000)
                    
                    form = page.locator("#go-link")
                    if form.count() > 0:
                        print("[*] Bypassing Timer & Submitting Gateway Form...")
                        form.evaluate("form => form.submit()")
                        
                        # Form submit hone ke baad final page redirect ka wait
                        page.wait_for_load_state("networkidle", timeout=30000)
                        page.wait_for_timeout(3000) # Thoda buffer time
                        break
                    else:
                        return "[-] Error: Gateway par #go-link form nahi mila."

            # Final URL extraction and cleanup
            final_url = page.url
            
            # Agar final link nested hai (e.g., ?url=https://...)
            if "url=" in final_url.lower():
                qs = parse_qs(urlparse(final_url).query)
                if 'url' in qs:
                    final_url = unquote(qs['url'][0])

            return final_url

        except Exception as e:
            return f"[-] Runtime Error: {str(e)}"
        finally:
            browser.close()

# ==========================================
# TELEGRAM HANDLERS
# ==========================================
@bot.message_handler(commands=['start', 'help'])
def start_msg(message):
    text = (
        "👑 **The Mods King Headless Bot Live!** 👑\n\n"
        "Bhai, mujhe koi bhi YorURL, Caslinks, ya Just2Earn ki link bhej, "
        "main background me Playwright chala ke tujhe final link dunga."
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: True)
def process_link(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "⚠️ Bhai valid link bhej (http:// ya https:// ke sath).")
        return

    msg_id = bot.reply_to(message, "⏳ *Intercepting Link...*\n_Headless engine Cloudflare ko bypass kar raha hai (10-15s lagenge)..._", parse_mode="Markdown").message_id
    
    start_time = time.time()
    result = headless_bypasser(url)
    elapsed = int(time.time() - start_time)

    # Validating if we actually bypassed it
    if result and result.startswith("http") and not any(x in result for x in ["whatsagrouplink", "newsuchnaonline", "thewiar", "go.just2earn", "go.yorurl"]):
        text = (
            "✅ **Bypass Successful!**\n\n"
            f"🔓 `{result}`\n\n"
            f"⏱ **Time:** {elapsed}s\n"
            "👑 _Powered By The Mods King_"
        )
    else:
        text = (
            "❌ **Bypass Failed!**\n\n"
            f"**Details:** {result}\n\n"
            "👑 _Powered By The Mods King_"
        )

    bot.edit_message_text(text, chat_id=message.chat.id, message_id=msg_id, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == "__main__":
    print("─"*50)
    print(" 🔥 THE MODS KING BOT IS RUNNING (PLAYWRIGHT MODE) 🔥")
    print("─"*50)
    bot.infinity_polling()
                      
