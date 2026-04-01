import logging
import httpx
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = '8441656381:AAG8ETJ-3NUOO4jvDAqxUS_AWicXKt_Dl_w'
ALLOWED_GROUP = 'osintt_ggs'
API_PIN = "541415"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Middleware: Group Check & Long Private Message
async def is_allowed(update: Update):
    if not update.message: return False
    
    if update.effective_chat.type == "private":
        long_private_msg = (
            "⚠️ <b>Access Denied: Restricted Module</b>\n\n"
            "This bot is a specialized OSINT tool designed exclusively for the "
            "<b>@osintt_ggs</b> community. Due to security protocols and API "
            "limitations, features are not available in private chats.\n\n"
            "<b>How to use:</b>\n"
            "1. Join the official group: @osintt_ggs\n"
            "2. Use the <code>/num</code> command followed by the mobile number.\n"
            "3. Ensure you follow the community guidelines for data searching.\n\n"
            "<i>Status: Unauthorized User Session Detected.</i>"
        )
        await update.message.reply_html(long_private_msg)
        return False
        
    if update.effective_chat.username != ALLOWED_GROUP:
        return False
    return True

# 1. Welcome Message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_allowed(update): return
    welcome_text = (
        "🛡️ <b>Welcome to VssTrue Bot!</b> 🛡️\n\n"
        "I am the official OSINT assistant for @osintt_ggs.\n"
        "Direct API Response Mode is now ACTIVE.\n\n"
        "🚀 <b>Available Commands:</b>\n"
        "🔹 <code>/num &lt;number&gt;</code> - Fetch Raw API Data\n"
        "🔹 <code>/stats</code> - System Status\n"
        "🔹 <code>/about</code> - Technical Info"
    )
    await update.message.reply_html(welcome_text)

# 2. /num Command (RAW RESPONSE MODE)
async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_allowed(update): return
    if not context.args:
        await update.message.reply_text("❌ Error: Please provide a number. Example: /num 9093614290")
        return

    user_num = ''.join(filter(str.isdigit, context.args[0]))
    wait_msg = await update.message.reply_text("🔍 <b>Fetching Raw Data from GBS Server...</b>", parse_mode='HTML')

    api_url = f"https://admin.gbssystems.com/public/storage/customer/28/api/index.php?number={user_num}&PIN={API_PIN}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, timeout=25.0)
            
            if response.status_code == 200:
                # API ka asli output (Raw Text)
                raw_api_output = response.text
                
                # Bot ab wahi bhejega jo API ne bheja hai (Code block format mein)
                final_response = (
                    f"✅ <b>API Raw Response:</b>\n\n"
                    f"<code>{raw_api_output}</code>\n\n"
                    f"📍 <b>Source:</b> GBS Systems Engine"
                )
                await wait_msg.delete()
                await update.message.reply_html(final_response)
            else:
                await wait_msg.edit_text(f"⚠️ <b>System Error:</b> API returned status code {response.status_code}")
    
    except Exception as e:
        await wait_msg.edit_text(f"❌ <b>Connection Error:</b> {str(e)}", parse_mode='HTML')

# 3. /stats Command
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_allowed(update): return
    await update.message.reply_html("📊 <b>System Statistics:</b>\nUptime: 100%\nMode: Raw Data Stream\nStatus: Secure ✅")

# 4. /about Command
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_allowed(update): return
    await update.message.reply_html(
        "🤖 <b>VssTrue Bot v3.5</b>\n"
        "Exclusively developed for @osintt_ggs.\n"
        "Direct API Integration (Bypassing Internal Formatting)."
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("num", num))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("about", about))
    
    print("VssTrue Bot is Running in RAW RESPONSE MODE...")
    app.run_polling()

if __name__ == '__main__':
    main()
