import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. خادم ويب لـ Render ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app_flask.run(host='0.0.0.0', port=port)

# --- 2. إعدادات البوت ---
TOKEN = "8381682425:AAGe4b02xncsIbiVt89cDjmuSojT2_NZ-8U"
MY_CHAT_ID = 5208623315

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك")

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MY_CHAT_ID:
        return

    user = update.effective_user
    text = update.message.text
    username_str = f"@{user.username}" if user.username else "لا يوجد"
    
    info_msg = (
        f"📩 رسالة جديدة من:\n"
        f"الاسم: {user.full_name}\n"
        f"المعرف: {username_str}\n"
        f"الـ ID: {user.id}\n\n"
        f"الرسالة:\n{text}"
    )
    
    sent_msg = await context.bot.send_message(
        chat_id=MY_CHAT_ID, 
        text=info_msg, 
        parse_mode="Markdown"
    )
    
    context.bot_data[sent_msg.message_id] = update.effective_chat.id
    await update.message.reply_text("تم الإرسال بنجاح")

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == MY_CHAT_ID and update.message.reply_to_message:
        original_msg_id = update.message.reply_to_message.message_id
        target_chat_id = context.bot_data.get(original_msg_id)
        
        if target_chat_id:
            await context.bot.send_message(
                chat_id=target_chat_id,
                text=update.message.text
            )
            await update.message.reply_text(" تم إرسال ردك بنجاح للمتابع!")
        else:
            await update.message.reply_text("⚠️ تعذر العثور على صاحب الرسالة.")

# --- 3. التشغيل ---
if __name__ == 'main':
    # تشغيل سيرفر الفلاسك في Thread منفصل
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    # تشغيل البوت عبر run_polling القياسي
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.REPLY, handle_user_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_admin_reply))
    
    app.run_polling(drop_pending_updates=True)
