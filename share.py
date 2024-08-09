import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaDocument, InputMediaVideo
import re

# Your bot token
BOT_TOKEN = '6182166277:AAGzDXMe4QBbG6fQcBFdBVygqf7ci7qkwQc'
# List of channel usernames or IDs where the bot is admin
CHANNEL_IDS = ['@RevRoxy', '@SrcEsp']
CHANNEL_NAMES = ['RevRoxy', 'SrcEsp']

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary to store user files and captions
user_files = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
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

    if user_id not in user_files:
        user_files[user_id] = {'photos': [], 'documents': [], 'videos': [], 'captions': {}}

    if message.content_type == 'document':
        file_id = message.document.file_id
        caption = message.caption if message.caption else ""
        user_files[user_id]['documents'].append(file_id)
        user_files[user_id]['captions'][file_id] = caption
    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        caption = message.caption if message.caption else ""
        user_files[user_id]['photos'].append(file_id)
        user_files[user_id]['captions'][file_id] = caption
    elif message.content_type == 'video':
        file_id = message.video.file_id
        caption = message.caption if message.caption else ""
        user_files[user_id]['videos'].append(file_id)
        user_files[user_id]['captions'][file_id] = caption

    bot.reply_to(message, "✅ File received! Use the '📤 Share Files' button or /share command to share them.")

@bot.message_handler(commands=['share'])
def share_files(message):
    user_id = message.from_user.id

    if user_id not in user_files or (not user_files[user_id]['photos'] and not user_files[user_id]['documents'] and not user_files[user_id]['videos']):
        bot.reply_to(message, "⚠️ No files to share. Please send files first.")
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for idx, channel_name in enumerate(CHANNEL_NAMES):
        button = InlineKeyboardButton(channel_name, callback_data=f'share_{CHANNEL_IDS[idx]}')
        keyboard.add(button)

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
        captions = user_files[user_id]['captions']

        for photo_id in files['photos']:
            caption = captions.get(photo_id, "")
            caption = replace_channel_info(caption, channel_id)
            media_group.append(InputMediaPhoto(photo_id, caption=caption))

        for video_id in files['videos']:
            caption = captions.get(video_id, "")
            caption = replace_channel_info(caption, channel_id)
            media_group.append(InputMediaVideo(video_id, caption=caption))

        for doc_id in files['documents']:
            caption = captions.get(doc_id, "")
            caption = replace_channel_info(caption, channel_id)
            media_group.append(InputMediaDocument(doc_id, caption=caption))

        if media_group:
            bot.send_media_group(channel_id, media_group)

        channel_name = CHANNEL_NAMES[CHANNEL_IDS.index(channel_id)] if channel_id in CHANNEL_IDS else channel_id
        bot.send_message(call.message.chat.id, f"✅ Files have been shared to {channel_name}.")

    except Exception as e:
        channel_name = CHANNEL_NAMES[CHANNEL_IDS.index(channel_id)] if channel_id in CHANNEL_IDS else channel_id
        bot.send_message(call.message.chat.id, f"❌ Failed to send to {channel_name}: {e}")

@bot.callback_query_handler(func=lambda call: call.data == 'finish_and_share_another')
def handle_finish_and_share_another(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id, "Finishing current file and preparing for another.")
    
    user_files[user_id] = {'photos': [], 'documents': [], 'videos': [], 'captions': {}}

    bot.send_message(call.message.chat.id, "✅ Finished with the current file. Please send another file to share.")

@bot.callback_query_handler(func=lambda call: call.data == 'help')
def callback_help(call):
    bot.send_message(call.message.chat.id, 
                     "🔹 **How to Use:**\n\n1. Send files (photos, videos, or documents) to me.\n2. Use the /share command or press the '📤 Share Files' button to share collected files to one or more channels.\n\n🔹 **Commands:**\n- `/start`: Start the bot and see the options.\n- `/help`: Get help about using the bot.")

def replace_channel_info(caption, channel_id):
    """
    Replace all occurrences of '@channelname' in the caption with '@mychannel',
    where '@mychannel' is the channel name where the message is being sent.
    """
    channel_name = CHANNEL_NAMES[CHANNEL_IDS.index(channel_id)] if channel_id in CHANNEL_IDS else "@Unknown"

    # Match '@channelname' but not 'click to copy' text
    def replace(match):
        return f'@{channel_name}' if match.group(1) else match.group(0)

    # Replace all occurrences of '@channelname' with '@mychannel'
    # Ensure not to replace '@somemonotext'
    caption = re.sub(r'(@\w+)', lambda match: replace(match), caption)
    return caption

# Start polling
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Bot encountered an error: {e}")
        print("Restarting in 5 seconds...")
        time.sleep(5)  # Wait before restarting to avoid rapid restart loops

