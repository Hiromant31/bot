import logging
from telegram import Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens the web app."""
    await update.message.reply_text(
        "Welcome! Click the button below to open the web application:",
        reply_markup={
            "keyboard": [[{
                "text": "Open WebApp",
                "web_app": {"url": "http://127.0.0.1:5008"}  # Replace with your actual web app URL
            }]],
            "resize_keyboard": True
        }
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Use /start to get the main menu with the WebApp button.")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6375500614:AAGXXU__GfV6ZJbeJr_PvhDDQdJVhVKDnEE").build()  # Replace with your actual bot token

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()