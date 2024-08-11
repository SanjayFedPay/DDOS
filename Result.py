import telebot
import requests
import json
import time
import logging

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = '6198878953:AAE4t1rQ6KXO2r12lig0Pwwdlnwr_iNut4I'
bot = telebot.TeleBot(BOT_TOKEN)

# Define the URL and headers for the API request
url = 'https://fastwin.trade/api_v1/smrcd'
headers = {
    'Cookie': 'GENXID=f17266f7166f6e148d4fd60795bf5265; UPD=Y; wPri=0; OWD=Y; rchash=Ph5084694f712950268; refcode=49858414742; userId=6287528864; pin=%C3%83%C3%A5%C3%B7%C3%A0%C3%A6%C3%AB%C3%92%C2%A3%C2%A0%C2%A1; pUrl=%23%2FTabIndex%3Findex%3DFastParity; usrli=1; rowid=26; uid=null; umob=null; unam=null; PHPSESSID=e71b42d2a5e93f21b8779ced677371c4; WallBal=8.40',
    'Content-Type': 'application/json',
}
data = {'i': '9202408111824', 'n': 'fs'}

# Store pattern length globally (default to 10)
pattern_length = 10

def fetch_data():
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        all_data = response.json()
        color_mapped = ["green" if int(entry['r']) % 2 != 0 else "red" for entry in all_data]
        return color_mapped
    except requests.RequestException as e:
        return f"Error fetching data: {e}"

def analyze_data(color_data):
    pattern_to_find = color_data[:pattern_length]
    reversed_pattern = pattern_to_find[::-1]  # Reverse the pattern
    found_patterns = find_all_patterns(color_data, pattern_to_find)
    
    after_counts = {'green': 0, 'red': 0}
    
    for _, next_color in found_patterns:
        if next_color:
            after_counts[next_color] += 1
    
    after_percentages = calculate_percentages(after_counts)
    
    last_opened_color = color_data[0] if color_data else "None"
    
    result_message = f"""
    
**Analysed Pattern:**
```Pattern: {reversed_pattern}```

🔵 **Last Opened Color:** `{last_opened_color.capitalize()}`

**Analysis Results:**

🔍 **Possible Upcoming Results:**
- **Green:** {after_counts['green']} ({after_percentages['green']:.2f}%)
- **Red:** {after_counts['red']} ({after_percentages['red']:.2f}%)

{'🟢 **Most Likely Result** : `Green`' if after_counts['green'] > after_counts['red'] else '🔴 **Most Likely Result** : `Red`'}

🚀 Click the button below to get more results or start over!
    """
    
    return result_message

def find_all_patterns(data, pattern):
    pattern_length = len(pattern)
    data_length = len(data)
    found_patterns = []

    i = pattern_length  # Start searching after the initial pattern
    while i <= data_length - pattern_length:
        if data[i:i + pattern_length] == pattern:
            next_index = i + pattern_length
            next_color = data[next_index] if next_index < data_length else None
            found_patterns.append((None, next_color))
            i = next_index  # Continue searching from the end of the current pattern
        else:
            i += 1  # Move to the next position

    return found_patterns

def calculate_percentages(counts):
    total = counts['green'] + counts['red']
    if total == 0:
        return {'green': 0.0, 'red': 0.0}
    return {
        'green': (counts['green'] / total) * 100,
        'red': (counts['red'] / total) * 100
    }

@bot.message_handler(commands=['start'])
def start(message):
    help_text = """
    📚 **Help Section** 📚

    Here are the commands you can use:

    - `/start` - Start the bot and get a welcome message along with help information.
    - `/setlength` - Set the pattern length for analysis. Send the new length as a number after this command.
    - `/help` - Get this help message.
    - Click the "Get Results" button to fetch and analyze results based on the current pattern length.

    🚀 Use the button below to get results or set the pattern length.
    """
    
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("Get Results", callback_data="get_results")
    markup.add(btn)
    
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['setlength'])
def set_length(message):
    bot.send_message(message.chat.id, "Please send the new pattern length as a number.")

@bot.message_handler(commands=['help'])
def help(message):
    help_text = """
    📚 **Help Section** 📚

    Here are the commands you can use:

    - `/start` - Start the bot and get a welcome message along with help information.
    - `/setlength` - Set the pattern length for analysis. Send the new length as a number after this command.
    - `/help` - Get this help message.
    - Click the "Get Results" button to fetch and analyze results based on the current pattern length.

    🚀 Use the button below to get results or set the pattern length.
    """
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("Get Results", callback_data="get_results")
    markup.add(btn)
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.isdigit())
def handle_pattern_length(message):
    global pattern_length
    pattern_length = int(message.text)
    bot.send_message(message.chat.id, f"Pattern length updated to {pattern_length}. Click the button below to get results.", reply_markup=telebot.types.InlineKeyboardMarkup().add(
        telebot.types.InlineKeyboardButton("Get Results", callback_data="get_results")
    ))

@bot.callback_query_handler(func=lambda call: call.data == "get_results")
def handle_results(call):
    color_data = fetch_data()
    if isinstance(color_data, str):
        bot.send_message(call.message.chat.id, color_data)
        return
    
    result_message = analyze_data(color_data)
    
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("Get Next Results", callback_data="get_results")
    markup.add(btn)
    
    bot.send_message(call.message.chat.id, result_message, parse_mode='Markdown', reply_markup=markup)

# Polling the bot with automatic restart on error
def start_polling():
    while True:
        try:
            bot.polling(none_stop=True, interval=2)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            time.sleep(5)  # Wait before restarting polling

# Start the bot
start_polling()
