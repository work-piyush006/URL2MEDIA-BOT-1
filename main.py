import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from datetime import datetime, timedelta

# ✅ BOT TOKEN setup: Env (Render) or fallback (Pydroid3)
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "7693918135:AAGKT8udJxAGcPFfhO6zuueHbg2MB-88n-w"
ADMIN_USERNAME = "@URL2MEDIA"

# ✅ Load premium users from file
def load_premium_users():
    if not os.path.exists("user_premium.txt"):
        return {}
    with open("user_premium.txt", "r") as f:
        return {line.split(":")[0]: line.strip().split(":")[1] for line in f if ":" in line}

# ✅ Check if user is premium
def is_premium(user_id):
    premium_users = load_premium_users()
    expiry = premium_users.get(str(user_id))
    if expiry:
        return datetime.strptime(expiry, "%Y-%m-%d") >= datetime.today()
    return False

# ✅ Main menu buttons
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Download Media", callback_data="download_media")],
        [InlineKeyboardButton("🎫 Redeem Coupons", callback_data="redeem_coupon")],
        [InlineKeyboardButton("💎 Get Premium", callback_data="get_premium")],
        [InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.strip('@')}")]
    ])

# ✅ /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 Welcome to URL2MEDIA_BOT!\n\n"
        "🧾 Convert media easily in seconds\n"
        "• 1 FREE download allowed\n"
        "• Upgrade to premium for ₹99/year\n"
        "• Have a COUPON CODE? REDEEM IT !!\n\n"
        "Choose an option:",
        reply_markup=main_menu_keyboard()
    )

# ✅ Handle media links or coupon code
def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    # If user was asked to enter a coupon
    if user_id in context.bot_data.get("awaiting_coupon", []):
        context.bot_data["awaiting_coupon"].remove(user_id)
        code = text.upper()
        valid = False

        if os.path.exists("coupon.txt"):
            with open("coupon.txt", "r") as f:
                coupons = f.read().splitlines()
            if code in coupons:
                with open("coupon_works.txt", "r") as f:
                    lines = f.read().splitlines()
                for line in lines:
                    if line.startswith(code):
                        if "PREMIUM" in line.upper():
                            expiry = (datetime.today() + timedelta(days=365)).strftime("%Y-%m-%d")
                            with open("user_premium.txt", "a") as f:
                                f.write(f"{user_id}:{expiry}\n")
                            update.message.reply_text("🎉 Coupon redeemed! You are now PREMIUM user until " + expiry)
                        else:
                            update.message.reply_text("✅ Coupon Applied: " + line.split("=")[1].strip())
                        valid = True
                        break
        if not valid:
            update.message.reply_text("❌ Invalid or expired coupon.")
        return

    # If user sends media link
    if "http" in text:
        if not is_premium(user_id):
            if os.path.exists("download.txt"):
                with open("download.txt", "r") as f:
                    count = sum(1 for line in f if line.startswith(str(user_id)))
            else:
                count = 0
            if count >= 1:
                update.message.reply_text(
                    "🚫 Free download limit reached. Please upgrade to premium.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💎 Get Premium", callback_data="get_premium")],
                        [InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.strip('@')}")]
                    ])
                )
                return
            else:
                with open("download.txt", "a") as f:
                    f.write(f"{user_id}:{text}\n")

        update.message.reply_text(
            "🎥 Media link received. Choose format:\n\n"
            "VIDEO - AUDIO format:\n"
            "[💎 1080p] [.mp4] 🔊🎥\n[🔸 720p] [.mp4] 🔊🎥\n[🔹 360p] [.mp4] 🔊🎥\n\n"
            "VIDEO - ONLY format:\n"
            "[💎 1080p] 🎥\n[🔸 720p] 🎥\n[🔹 360p] 🎥\n\n"
            "AUDIO - ONLY format:\n"
            "[💎 1080p] [.mp3] 🔊\n[🔸 720p] [.mp3] 🔊\n[🔹 360p] [.mp3] 🔊",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ])
        )

# ✅ Handle all button callbacks
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    query.answer()

    if data == "download_media":
        query.message.reply_text("📥 Send your media link to download.\n\n✅ 1 FREE download available.")
    elif data == "get_premium":
        if not os.path.exists("user.txt"):
            open("user.txt", "w").close()
        with open("user.txt", "r") as f:
            if str(user_id) not in f.read():
                with open("user.txt", "a") as f2:
                    f2.write(f"{user_id}\n")
        context.bot.send_photo(
            chat_id=user_id,
            photo=open("Qr.png", "rb"),
            caption="💎 Upgrade to PREMIUM for ₹99/year\n\n📲 Scan the QR to pay via UPI.\n\nOr contact admin to activate manually.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.strip('@')}")]
            ])
        )
    elif data == "redeem_coupon":
        query.message.reply_text(
            "🎫 Redeem Coupon\n\n"
            "🪙 Please send your coupon code now!!\n\n"
            "✨ Get discount on premium purchase\n🎁 Get free download\n🚀 Or many moreee...",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ])
        )
        context.bot_data.setdefault("awaiting_coupon", []).append(user_id)
    elif data == "back_to_menu":
        query.message.reply_text(
            "👋 Welcome back to the main menu!\n\n"
            "🤖 Welcome to URL2MEDIA_BOT!\n\n"
            "🧾 Convert media easily in seconds\n"
            "• 1 FREE download allowed\n"
            "• Upgrade to premium for ₹99/year\n"
            "• Have a COUPON CODE? REDEEM IT !!\n\n"
            "Choose an option:",
            reply_markup=main_menu_keyboard()
        )

# ✅ Main function
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "7693918135:AAGKT8udJxAGcPFfhO6zuueHbg2MB-88n-w"

def main():
    if not BOT_TOKEN or not BOT_TOKEN.startswith("769"):
        raise ValueError("❌ BOT_TOKEN is not set correctly!")

    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🤖 Bot is running... Waiting for messages")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
