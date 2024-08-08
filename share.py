import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaDocument, InputMediaVideo

# Your bot token
BOT_TOKEN = '6182166277:AAGzDXMe4QBbG6fQcBFdBVygqf7ci7qkwQc'
# List of channel usernames or IDs where the bot is admin
CHANNEL_IDS = ['@RevRoxy', '@SrcEsp']
CHANNEL_NAMES = ['RevRoxy', 'SrcEsp']

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary to store user files
user_files = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Create an inline keyboard with buttons
    keyboard = InlineKeyboardMarkup(row_width=2)  # Arrange buttons in rows of 2
    share_button = InlineKeyboardButton("📤 Share Files", callback_data='share_files')
    help_button = InlineKeyboardButton("❓ Help", callback_data='help')
    keyboard.add(share_button, help_button)

    bot.send_message(message.chat.id, 
                     "Welcome to the File Sharing Bot! 🎉\n\nSend me files or forward messages, and use the buttons below to interact with the bot.",
                     reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, 
                     "🔹 **How to Use:**\n\n1. Send files (photos, videos, or documents) to me.\n2. Use the /share command or press the '📤 Share Files' button to share collected files to one or more channels.\n\n🔹 **Commands:**\n- `/start`: Start the bot and see the options.\n- `/help`: Get help about using the bot.")

@bot.message_handler(content_types=['document', 'photo', 'video'])
def handle_file(message):
    user_id = message.from_user.id

    # Initialize user files list if not already present
    if user_id not in user_files:
        user_files[user_id] = {'photos': [], 'documents': [], 'videos': []}

    # Collect the file ID based on content type
    if message.content_type == 'document':
        file_id = message.document.file_id
        user_files[user_id]['documents'].append(file_id)
    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        user_files[user_id]['photos'].append(file_id)
    elif message.content_type == 'video':
        file_id = message.video.file_id
        user_files[user_id]['videos'].append(file_id)

    # Notify the user that the file is being processed
    bot.reply_to(message, "✅ File received! Use the '📤 Share Files' button or /share command to share them.")

@bot.message_handler(commands=['share'])
def share_files(message):
    user_id = message.from_user.id

    if user_id not in user_files or (not user_files[user_id]['photos'] and not user_files[user_id]['documents'] and not user_files[user_id]['videos']):
        bot.reply_to(message, "⚠️ No files to share. Please send files first.")
        return

    # Create inline keyboard for channel selection
    keyboard = InlineKeyboardMarkup(row_width=1)
    for idx, channel_name in enumerate(CHANNEL_NAMES):
        button = InlineKeyboardButton(channel_name, callback_data=f'share_{CHANNEL_IDS[idx]}')
        keyboard.add(button)

    # Add a "Finish and Share Another File" button
    finish_button = InlineKeyboardButton("Finish and Share Another File", callback_data='finish_and_share_another')
    keyboard.add(finish_button)

    bot.send_message(message.chat.id, 
                     "Please select the channel where you want to share your files, or choose to finish and share another file:",
                     reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('share_'))
def handle_channel_share(call):
    channel_id = call.data.split('_', 1)[1]
    user_id = call.from_user.id

    if user_id not in user_files or (not user_files[user_id]['photos'] and not user_files[user_id]['documents'] and not user_files[user_id]['videos']):
        bot.answer_callback_query(call.id, "⚠️ No files to share. Please send files first.")
        return

    files = user_files[user_id]
    bot.answer_callback_query(call.id, "🔄 Sharing your files...")

    try:
        media_group = []

        # Add photos to media group
        for photo_id in files['photos']:
            media_group.append(InputMediaPhoto(photo_id))

        # Add videos to media group
        for video_id in files['videos']:
            media_group.append(InputMediaVideo(video_id))

        # Add documents to media group
        for doc_id in files['documents']:
            media_group.append(InputMediaDocument(doc_id))

        if media_group:
            bot.send_media_group(channel_id, media_group)

        # Safely retrieve the channel name
        channel_name = CHANNEL_NAMES[CHANNEL_IDS.index(channel_id)] if channel_id in CHANNEL_IDS else channel_id
        bot.send_message(call.message.chat.id, f"✅ Files have been shared to {channel_name}.")

    except Exception as e:
        # Safely retrieve the channel name
        channel_name = CHANNEL_NAMES[CHANNEL_IDS.index(channel_id)] if channel_id in CHANNEL_IDS else channel_id
        bot.send_message(call.message.chat.id, f"❌ Failed to send to {channel_name}: {e}")

@bot.callback_query_handler(func=lambda call: call.data == 'finish_and_share_another')
def handle_finish_and_share_another(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id, "Finishing current file and preparing for another.")
    
    # Clear the user's current files after sharing
    user_files[user_id] = {'photos': [], 'documents': [], 'videos': []}

    bot.send_message(call.message.chat.id, "✅ Finished with the current file. Please send another file to share.")
    # The user can now send another file, which will be handled by the `handle_file` function.

@bot.callback_query_handler(func=lambda call: call.data == 'help')
def callback_help(call):
    bot.send_message(call.message.chat.id, 
                     "🔹 **How to Use:**\n\n1. Send files (photos, videos, or documents) to me.\n2. Use the /share command or press the '📤 Share Files' button to share collected files to one or more channels.\n\n🔹 **Commands:**\n- `/start`: Start the bot and see the options.\n- `/help`: Get help about using the bot.")

# Start polling
bot.polling(none_stop=True)
