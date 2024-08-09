import telebot
import requests
from telebot import types
import time
from threading import Timer

BOT_TOKEN = '6489358174:AAH2L3e-oHlyGFwe5mugwV9T26o-3G9w508'
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}
user_last_interaction = {}
auto_find_next_timers = {}
processing_status = {}
message_state = {}

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
        periods = response.json()[:15]
        return periods
    except Exception as e:
        return f"Error: {e}"

def check_periods_for_input(periods, input_value):
    input_str = str(input_value)
    for item in periods:
        period_str = str(item.get('p', ''))
        number_str = str(item.get('r', ''))
        if input_str in period_str or input_str in number_str:
            return item
    return None

def background_processing(chat_id, i_value, message_id=None):
    start_time = time.time()
    found = False

    processing_message = bot.send_message(chat_id, "🔄 Processing Upcoming Result...")
    processing_message_id = processing_message.message_id
    processing_status[chat_id] = processing_message_id

    message_state[processing_message_id] = {
        'content': "🔄 Processing your request...",
        'markup': None
    }

    while not found and time.time() - start_time < 30:
        if chat_id in processing_status:
            periods = get_latest_periods(i_value)
            item = check_periods_for_input(periods, i_value)

            if item:
                found = True
                try:
                    number = int(item['r'])
                    color_emoji = "🔴" if number % 2 == 0 else "🟢"
                    result_message = f"✅ Result Found!\n\n📅 Period: {item['p']}\n🔢 Number: {item['r']}\n🎨 Color: {color_emoji}"
                    markup = types.InlineKeyboardMarkup()
                    stop_btn = types.InlineKeyboardButton(text="🚫 Stop", callback_data="stop_processing")
                    markup.add(stop_btn)
                    if message_state.get(processing_message_id, {}).get('content') != result_message or \
                       message_state.get(processing_message_id, {}).get('markup') != markup:
                        bot.edit_message_text(result_message, chat_id, processing_message_id, reply_markup=markup)
                        message_state[processing_message_id] = {'content': result_message, 'markup': markup}
                    auto_find_next_timers[chat_id] = Timer(0, auto_find_next, args=[chat_id, i_value + 1])
                    auto_find_next_timers[chat_id].start()
                except Exception as e:
                    print(f"Error editing message: {e}")
                break

            progress = int((time.time() - start_time) / 30 * 20)
            progress_bar = "[" + "=" * progress + "-" * (20 - progress) + "]"
            percentage = int((progress / 20) * 100)
            animation_text = f"🔄 Processing {progress_bar} {percentage}%"
            
            try:
                if message_state.get(processing_message_id, {}).get('content') != animation_text:
                    bot.edit_message_text(animation_text, chat_id, processing_message_id)
                    message_state[processing_message_id] = {'content': animation_text, 'markup': None}
            except Exception as e:
                print(f"Error editing message: {e}")

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
        #bot.send_message(chat_id, f"🔍 Fetching next result for period {i_value}...")
        user_data[chat_id] = i_value
        background_processing(chat_id, i_value)

def check_last_interaction(chat_id):
    current_time = time.time()
    last_time = user_last_interaction.get(chat_id, 0)
    if current_time - last_time > 60:
        return True
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if chat_id in processing_status:
        del processing_status[chat_id]
        bot.send_message(chat_id, "🚫 Processing stopped. Restarting from the beginning...")
        if chat_id in auto_find_next_timers:
            auto_find_next_timers[chat_id].cancel()
            del auto_find_next_timers[chat_id]
    msg = bot.send_message(chat_id, '👋 Welcome to the Future Results Bot!\n Made By Sanjay_Src \n Join Telegram : @SrcEsp\n🔍 Please Enter Last 3 Digits of the Period !')
    bot.register_next_step_handler(msg, process_i_value)
    user_last_interaction[chat_id] = time.time()

@bot.callback_query_handler(func=lambda call: call.data.startswith("find_next_"))
def handle_find_next(call):
    chat_id = call.message.chat.id
    i_value = int(call.data.split("_")[2])
    user_data[call.from_user.id] = i_value
    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
    if chat_id in auto_find_next_timers:
        auto_find_next_timers[chat_id].cancel()
        del auto_find_next_timers[chat_id]
    background_processing(chat_id, i_value + 1, call.message.message_id)
    user_last_interaction[chat_id] = time.time()

@bot.callback_query_handler(func=lambda call: call.data == "stop_processing")
def handle_stop_processing(call):
    chat_id = call.message.chat.id
    if chat_id in processing_status:
        del processing_status[chat_id]
        bot.edit_message_text("🚫 Processing stopped.\n\nTo start again, click /start.", chat_id, call.message.message_id)
        if chat_id in auto_find_next_timers:
            auto_find_next_timers[chat_id].cancel()
            del auto_find_next_timers[chat_id]

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

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Bot encountered an error: {e}")
        print("Restarting in 5 seconds...")
        time.sleep(5)  # Wait before restarting to avoid rapid restart loops

