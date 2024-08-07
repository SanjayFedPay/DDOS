import telebot
import requests
from telebot import types
import time
from threading import Timer

# Your bot token from BotFather
BOT_TOKEN = '6182166277:AAGzDXMe4QBbG6fQcBFdBVygqf7ci7qkwQc'
bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary to store user data and timers
user_data = {}
user_last_interaction = {}
auto_find_next_timers = {}
processing_status = {}  # Track processing status for each user
message_state = {}  # Track the state of messages to prevent redundant updates

# Function to get latest periods
def get_latest_periods(i_value):
    try:
        url = 'https://fastwin.trade/api_v1/smrcd'
        headers = {
            'Cookie': 'GENXID=f17266f7166f6e148d4fd60795bf5265; UPD=Y; wPri=0; OWD=Y; rchash=Ph5084694f712950268; refcode=49858414742; userId=6287528864; pin=%C3%83%C3%A5%C3%B7%C3%A0%C3%A6%C3%AB%C3%92%C2%A3%C2%A0%C2%A1; pUrl=%23%2FTabIndex%3Findex%3DFastParity; usrli=1; rowid=26; uid=null; umob=null; unam=null; PHPSESSID=e71b42d2a5e93f21b8779ced677371c4; WallBal=8.40',
            'Content-Type': 'application/json',
        }
        data = {
            'i': i_value,
            'n': 'fs'
        }
        response = requests.post(url, json=data, headers=headers)
        periods = response.json()[:5]  # Get the top 5 items
        return periods
    except Exception as e:
        return f"Error: {e}"

# Function to check if any period contains the user's input
def check_periods_for_input(periods, input_value):
    input_str = str(input_value)  # Convert input_value to a string
    for item in periods:
        period_str = str(item.get('p', ''))
        number_str = str(item.get('r', ''))
        if input_str in period_str or input_str in number_str:
            return item  # Return the item that matches
    return None

# Function to handle background processing
def background_processing(chat_id, i_value, message_id=None):
    start_time = time.time()
    found = False
    update_interval = 0.02  # Update every 0.02 seconds

    # Send initial processing message
    processing_message = bot.send_message(chat_id, "🔄 Processing your request...")
    processing_message_id = processing_message.message_id
    processing_status[chat_id] = processing_message_id

    # Initialize message state
    message_state[processing_message_id] = {
        'content': "🔄 Processing your request...",
        'markup': None
    }

    # Track the last progress to avoid redundant edits
    last_progress = -1

    while not found and time.time() - start_time < 30:
        if chat_id in processing_status:
            periods = get_latest_periods(i_value)
            item = check_periods_for_input(periods, i_value)

            if item:
                found = True
                try:
                    # Determine the color based on the number
                    number = int(item['r'])
                    color_emoji = "🔴" if number % 2 == 0 else "🟢"

                    # Send the result message with the "Stop" button
                    result_message = f"✅ Result Found!\n\n📅 Period: {item['p']}\n🔢 Number: {item['r']}\n🎨 Color: {color_emoji}"
                    markup = types.InlineKeyboardMarkup()
                    stop_btn = types.InlineKeyboardButton(text="🚫 Stop", callback_data="stop_processing")
                    markup.add(stop_btn)
                    if message_state.get(processing_message_id, {}).get('content') != result_message or \
                       message_state.get(processing_message_id, {}).get('markup') != markup:
                        bot.edit_message_text(result_message, chat_id, processing_message_id, reply_markup=markup)
                        message_state[processing_message_id] = {'content': result_message, 'markup': markup}
                    auto_find_next_timers[chat_id] = Timer(5, auto_find_next, args=[chat_id, i_value + 1])
                    auto_find_next_timers[chat_id].start()
                except Exception as e:
                    print(f"Error editing message: {e}")
                break

            # Update processing message with progress
            progress = int((time.time() - start_time) / 30 * 20)  # 20 steps for the progress bar
            progress_bar = "[" + "=" * progress + "-" * (20 - progress) + "]"
            percentage = int((progress / 20) * 100)
            animation_text = f"🔄 Processing {progress_bar} {percentage}%"
            
            if progress != last_progress:
                try:
                    if message_state.get(processing_message_id, {}).get('content') != animation_text:
                        bot.edit_message_text(animation_text, chat_id, processing_message_id)
                        message_state[processing_message_id] = {'content': animation_text, 'markup': None}
                    last_progress = progress
                except Exception as e:
                    print(f"Error editing message: {e}")

          #  time.sleep(update_interval)  # Avoid blocking the bot

    if not found and chat_id in processing_status:
        try:
            no_result_message = "🔍 No matching periods found. Please try again later."
            if message_state.get(processing_message_id, {}).get('content') != no_result_message:
                bot.edit_message_text(no_result_message, chat_id, processing_message_id)
                message_state[processing_message_id] = {'content': no_result_message, 'markup': None}
        except Exception as e:
            print(f"Error editing message: {e}")
        del processing_status[chat_id]

def auto_find_next(chat_id, i_value):
    if chat_id in auto_find_next_timers:
        del auto_find_next_timers[chat_id]
        # Notify the user that auto-find is in progress
        bot.send_message(chat_id, "⏳ Auto Find is in progress. Fetching the next result...")
        # Automatically find the next result if user doesn't click
        user_data[chat_id] = i_value  # Update user data with new value
        # Start background processing for new value
        background_processing(chat_id, i_value, None)

def check_last_interaction(chat_id):
    """ Check if the last interaction was more than 1 minute ago """
    current_time = time.time()
    last_time = user_last_interaction.get(chat_id, 0)
    if current_time - last_time > 60:
        return True
    return False

# Command handler for /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    # Stop any ongoing processing
    if chat_id in processing_status:
        del processing_status[chat_id]
        bot.send_message(chat_id, "🚫 Processing stopped. Restarting from the beginning...")
        if chat_id in auto_find_next_timers:
            auto_find_next_timers[chat_id].cancel()
            del auto_find_next_timers[chat_id]
    # Prompt for initial input
    msg = bot.send_message(chat_id, '👋 Welcome to the Future Results Bot!\n Made By Sanjay_Src \n Join Telegram : @SrcEsp\n🔍 Please Enter Last 3 Digits of the Period !')
    bot.register_next_step_handler(msg, process_i_value)
    user_last_interaction[chat_id] = time.time()

# Callback query handler for "Find Next" button
@bot.callback_query_handler(func=lambda call: call.data.startswith("find_next_"))
def handle_find_next(call):
    chat_id = call.message.chat.id
    i_value = int(call.data.split("_")[2])
    user_data[call.from_user.id] = i_value  # Update user data with new value
    # Remove the old "Find Next" button
    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
    # Cancel the auto-find-next timer if it exists
    if chat_id in auto_find_next_timers:
        auto_find_next_timers[chat_id].cancel()
        del auto_find_next_timers[chat_id]
    # Start background processing for new value
    background_processing(chat_id, i_value + 1, call.message.message_id)
    user_last_interaction[chat_id] = time.time()

# Callback query handler for "Stop" button
@bot.callback_query_handler(func=lambda call: call.data == "stop_processing")
def handle_stop_processing(call):
    chat_id = call.message.chat.id
    # Cancel processing if active
    if chat_id in processing_status:
        del processing_status[chat_id]
        # Remove the "Stop" button and display the message
        bot.edit_message_text("🚫 Processing stopped.\n\nTo start again, click /start.", chat_id, call.message.message_id)
        # Cancel any auto-find-next timer for the user
        if chat_id in auto_find_next_timers:
            auto_find_next_timers[chat_id].cancel()
            del auto_find_next_timers[chat_id]

# Function to process the 'i' value input
def process_i_value(message):
    chat_id = message.chat.id
    i_value = message.text.strip()
    if i_value.isdigit():
        i_value = int(i_value)
        user_data[chat_id] = i_value
        background_processing(chat_id, i_value)
    else:
        msg = bot.send_message(chat_id, "🚫 Invalid input. Please enter a valid number.")
        bot.register_next_step_handler(msg, process_i_value)

# Polling loop
bot.polling(none_stop=True, interval=2)
