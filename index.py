import telebot
from telebot import types
import os
from datetime import datetime

# Initialize bot with your token
TOKEN = 'YOUR_BOT_TOKEN'  # Replace with your actual bot token
bot = telebot.TeleBot(TOKEN)

# Sample product database (you can replace this with a real database)
products = {
    '1': {'name': 'Product 1', 'price': 10.99, 'description': 'Description of product 1'},
    '2': {'name': 'Product 2', 'price': 20.99, 'description': 'Description of product 2'},
    '3': {'name': 'Product 3', 'price': 15.99, 'description': 'Description of product 3'},
}

# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('📝 View Products', '🛒 My Cart')
    markup.row('💬 Contact Support', '❓ Help')
    
    welcome_text = f"Welcome to our Sales Bot!\n\nWhat would you like to do?"
    bot.reply_to(message, welcome_text, reply_markup=markup)

# View products handler
@bot.message_handler(func=lambda message: message.text == '📝 View Products')
def show_products(message):
    for product_id, product in products.items():
        markup = types.InlineKeyboardMarkup()
        add_to_cart = types.InlineKeyboardButton(
            "Add to Cart", 
            callback_data=f"add_{product_id}"
        )
        markup.add(add_to_cart)
        
        product_text = f"*{product['name']}*\n"
        product_text += f"Price: ${product['price']}\n"
        product_text += f"Description: {product['description']}"
        
        bot.send_message(
            message.chat.id,
            product_text,
            parse_mode='Markdown',
            reply_markup=markup
        )

# Callback query handler for adding products to cart
@bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
def add_to_cart_callback(call):
    product_id = call.data.split('_')[1]
    if product_id in products:
        product = products[product_id]
        bot.answer_callback_query(
            call.id,
            f"{product['name']} added to cart!",
            show_alert=True
        )

# Help command handler
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
*Available Commands:*
/start - Start the bot
/help - Show this help message
    
*Available Buttons:*
📝 View Products - Browse our products
🛒 My Cart - View your shopping cart
💬 Contact Support - Get help from our team
❓ Help - Show help information
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

# Contact support handler
@bot.message_handler(func=lambda message: message.text == '💬 Contact Support')
def contact_support(message):
    support_text = "Need help? Contact our support team at support@example.com"
    bot.reply_to(message, support_text)

# Default handler for unknown commands
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "I don't understand that command. Please use the menu or type /help for available commands.")

# Start the bot
if __name__ == "__main__":
    print("Bot started...")
    bot.infinity_polling()