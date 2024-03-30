from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters,
                CallbackContext)
import ssl
import random
import mysql.connector
import requests
import uuid


from pytube import YouTube
from telebot import TeleBot
import telebot
from telebot import types
import configparser
import logging

from ChatGPT_HKBU import HKBU_ChatGPT

ssl._create_default_https_context = ssl._create_stdlib_context
   
global bot
bot = telebot.TeleBot('6972742316:AAGfE5-aYPEoQN4SF1J5mgaqgm5oi9AQl0Q')
global_review = "" 
global_url = ""  
global_desc = "" 
global_photo_data = {'key1': {'description': 'Description 1', 'url': 'URL 1'}}


def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    global bot
    bot = telebot.TeleBot(config['TELEGRAM']['ACCESS_TOKEN'])
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    # You can set this logging module, so you will know when
    # and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
    # register a dispatcher to handle message: here we register an echo dispatcher
    #echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    #dispatcher.add_handler(echo_handler)

    # dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("view", view_theme))
    dispatcher.add_handler(CommandHandler("review", writeReview_callback))
    dispatcher.add_handler(CallbackQueryHandler(message_handler))
    # To start the bot:
    updater.start_polling()
    updater.idle()

def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')
def hello(update: Update, context: CallbackContext) -> None: 
    """Send a message when the command /hello is issued.""" 
    try:
        logging.info(context.args[0])
        msg = context.args[0] # /hello keyword <-- this should store the keyword
        update.message.reply_text('Good day, ' + msg + ' ! ' )
    except (IndexError, ValueError): 
         update.message.reply_text('Usage: /hello <keyword>')
def start_command(update: Update, context: CallbackContext) -> None: 
    """Send a message when the command /start is issued.""" 
    try:
        global bot
        #markup = types.InlineKeyboardMarkup(row_width=1)
        #iron = types.InlineKeyboardButton('1 kilo of iron', callback_data= 'answer_iron')
        #cotton = types.InlineKeyboardButton('1 kilo of cotton', callback_data= 'answer_cotton')
        #same = types.InlineKeyboardButton( 'same weight', callback_data= 'answer_same')
        #no_answer = types.InlineKeyboardButton('no correct answer', callback_data= 'no_answer')
        #markup.add(iron, cotton, same, no_answer)
        #bot.send_message(update.effective_chat.id,' Welcome to CC chatbot? \n Please select the below function', reply_markup=markup)
	#InlineKeyboard
        keyboard_1 = InlineKeyboardMarkup([
            [
              InlineKeyboardButton("View Hong Kong Photo", callback_data="view_hongkong")
             ],
	     [
              InlineKeyboardButton("View Other Photo", callback_data="view_other")
             ],
                [
              InlineKeyboardButton("View Cooking Video", callback_data="view_cooking")
             ], [
                 InlineKeyboardButton("Read TV Show Review", callback_data="read_review")
             ], [
                 InlineKeyboardButton("Write TV Show Review", callback_data="write_review")
             ]
         ])
        update.message.reply_text(
        text=' Welcome to CC chatbot? \n Please select the below function', reply_markup=keyboard_1)

    except (IndexError, ValueError): 
        update.message.reply_text('Usage: /hello <keyword>')

def message_handler(update: Update, context: CallbackContext):
    global bot
    if update.callback_query.data == 'read_review':
        readview_callback(update, context)



    elif update.callback_query.data == 'write_review':
       bot.send_message(update.effective_chat.id,'Usage: /review <TV Show>, <Your name>, <Rating[1-5]>, <Your Review> \n\nexample: /review Sherlock, Olivia, 4, Brilliant detective series')
    elif update.callback_query.data == 'translate_english':
        translate_chatgpt(update, context,'EN')
    elif update.callback_query.data == 'translate_chinese':
        translate_chatgpt(update, context,'TC')
    elif 'translate_english_photo' in update.callback_query.data :
        translate_photo(update, context,'EN', update.callback_query.data)
    elif 'translate_chinese_photo' in update.callback_query.data :
        translate_photo(update, context,'TC', update.callback_query.data)
    elif update.callback_query.data == 'view_hongkong':
        view_hongKong(update, context)
    elif update.callback_query.data == 'view_other':
        bot.send_message(update.effective_chat.id,'Usage: /view <Target theme> \n\nexample: /view hiking in Hong kong')    
    elif update.callback_query.data == 'view_cooking':
	# List of YouTube URLs
        youtube_urls = [
        "https://www.youtube.com/watch?v=TwZ0J6ED_2c",
        "https://www.youtube.com/watch?v=61tFikJm0XM",
        "https://www.youtube.com/watch?v=jKHnr9n2Cw0",
	"https://www.youtube.com/watch?v=zGmTZ6bXiSs",
        "https://www.youtube.com/watch?v=vGE-RfP6KRE",
        "https://www.youtube.com/watch?v=a3EYQARJkLk"
        ]
        # Choose a random YouTube URL
        random_url = random.choice(youtube_urls)
        # Assign the YouTube URL to the 'yt' variable
        yt = YouTube(random_url)
        video = yt.streams.filter(file_extension="mp4").get_by_resolution("360p").download("./tmp")
        bot.send_video(update.effective_chat.id, open(video, 'rb'), width=1280, height=720)


def readview_callback(update, context):
    
    global global_review
    # Establish a connection to the MySQL database
    cnx = mysql.connector.connect(
        user="shun",
        password="Qwer1234",
        host="shun.mysql.database.azure.com",
        port=3306,
        database="chatbot",
        ssl_disabled=True,
    )
    # Create an empty string to store the retrieved data
    review_data_string = ""

    # Create a cursor object to execute SQL queries
    cursor = cnx.cursor()

    # Define the SQL query to retrieve data from the TV_Reviews table
    query = "SELECT tv_show, reviewer_name, rating , review_text FROM TV_Reviews"

    # Execute the query
    cursor.execute(query)

    # Fetch all the rows returned by the query
    rows = cursor.fetchall()

   

    # Iterate over the rows and append the data to the string
    for row in rows:
        tv_show = row[0]
        reviewer_name = row[1]
        rating = row[2] 

        # Calculate the number of full stars and half star
        full_stars = int(rating)
        half_star = int((rating - full_stars) * 2)

	# Generate the star string
        star_string = "\u2605" * full_stars + "\u00BD" * half_star
  
        review_text = row[3]
        review_data_string += (
            f"<b>{tv_show}</b>\nReviewer: {reviewer_name}\nRating: {star_string}\nReview: {review_text}\n\n"
        )

    # Print the string containing the retrieved data
    #print(review_data_string)
    

    # Close the cursor and the database connection
    cursor.close()
    cnx.close()

   
    markup = types.InlineKeyboardMarkup(row_width=2)
    translate_english = types.InlineKeyboardButton('Translate to English', callback_data= 'translate_english')
    translate_chinese = types.InlineKeyboardButton('Translate to Chinese', callback_data= 'translate_chinese')
    markup.add(translate_english, translate_chinese)
    global_review= review_data_string
    bot.send_message(update.effective_chat.id,'The TV reviews as below:\n\n'+ review_data_string ,parse_mode='HTML', reply_markup=markup)
   
    #bot.send_message(update.effective_chat.id,'The TV reviews as below:\n\n'+ review_data_string, parse_mode='HTML', reply_markup= reply_markup)
    #update.message.reply_text(text='The TV reviews as below:\n\n'+ review_data_string', parse_mode='HTML', reply_markup=keyboard_1)
    
def writeReview_callback(update, context):
    try:
        result = ' '.join(context.args)
        substrings = result.split(",")
        if len(substrings) > 4:
    	    substrings[3] = ', '.join(substrings[3:])
	    # Remove the remaining items from the list
    	    del substrings[4:]
    
        tvshow=substrings[0]
        reviewer=substrings[1]
        rating=substrings[2]
        review=substrings[3]

        # Establish a connection to the MySQL database
        cnx = mysql.connector.connect(
            user="shun",
            password="Qwer1234",
            host="shun.mysql.database.azure.com",
            port=3306,
            database="chatbot",
            ssl_disabled=True
        )

        # Create a cursor object to execute SQL queries
        cursor = cnx.cursor()

        # Define the SQL query to insert data into the TV_Reviews table
        query = "INSERT INTO TV_Reviews ( tv_show, reviewer_name, rating, review_text) VALUES (%s, %s, %s, %s)"

        # Define the values to be inserted
        values = (tvshow, reviewer, rating, review)

        # Execute the query with the values
        cursor.execute(query, values)

        # Commit the changes to the database
        cnx.commit()

        # Close the cursor and the database connection
        cursor.close()
        cnx.close()

        # Calculate the number of full stars and half star
        full_stars = int(rating)
        half_star = int((int(rating) - full_stars) * 2)

	# Generate the star string
        star_string = "\u2605" * full_stars + "\u00BD" * half_star
        bot.send_message(update.effective_chat.id,f"Your review has been successfully added.\n\n<b>{tvshow}</b>\nReviewer:{reviewer}\nRating:{star_string}\nReview:{review}\n\n", parse_mode='HTML')
    except (IndexError, ValueError): 
        update.message.reply_text('Usage: /review <TV Show>, <Your name>, <Rating[1-5]>, <Your Review> \n\nexample: /review Sherlock, Olivia, 4, Brilliant detective series')

def view_theme(update, context):
    global global_desc
    global global_url

    try:
        if len(context.args) > 0:
            result = ' '.join(context.args)
            # Make a request to the Unsplash API
            response = requests.get('https://api.unsplash.com/search/photos/?client_id=qRtKMXiMZ16w0zncez6BHFzV0UXDQ4bnyFllVJ2H_7g&per_page=1&query='+ result)
            data = response.json()

            # Retrieve the small photo URL from the API response
            photo_url = data['results'][0]['urls']['small']

            # Load the image file from the retrieved URL
            photo_response = requests.get(photo_url)
            photo = photo_response.content
            global chatgpt
            key = str(uuid.uuid4())
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            translate_english = types.InlineKeyboardButton('Translate to English', callback_data= 'translate_english_photo_'+ key)
            translate_chinese = types.InlineKeyboardButton('Translate to Chinese', callback_data= 'translate_chinese_photo_'+ key)
            markup.add(translate_english, translate_chinese)
            reply_message = chatgpt.submit('Please use 30 words to descript what is '+ result)
            global_desc = reply_message
            global_url = photo_url
            global_photo_data[key] = {'description': reply_message, 'url': photo_url}
            # Send the image with a caption
            bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption= reply_message, reply_markup= markup)
            clearphotodata()
        else:
            update.message.reply_text('Usage: /view <Target theme> \n\nexample: /view hiking in Hong kong')
    except (IndexError, ValueError): 
        update.message.reply_text('Usage: /view <Target theme> \n\nexample: /view hiking in Hong kong')
 


def view_hongKong(update, context):
    global global_desc
    global global_url

    # Make a request to the Unsplash API
    response = requests.get('https://api.unsplash.com/search/photos/?client_id=qRtKMXiMZ16w0zncez6BHFzV0UXDQ4bnyFllVJ2H_7g&per_page=1&query=hongkong')
    data = response.json()

    # Retrieve the small photo URL from the API response
    photo_url = data['results'][0]['urls']['small']

    # Load the image file from the retrieved URL
    photo_response = requests.get(photo_url)
    photo = photo_response.content
    global chatgpt
    markup = types.InlineKeyboardMarkup(row_width=2)
    key = str(uuid.uuid4())
    translate_english = types.InlineKeyboardButton('Translate to English', callback_data= 'translate_english_photo_'+ key)
    translate_chinese = types.InlineKeyboardButton('Translate to Chinese', callback_data= 'translate_chinese_photo_'+ key)
    markup.add(translate_english, translate_chinese)
    reply_message = chatgpt.submit('Please use 30 words to descript what is Hong Kong')
    global_desc = reply_message
    global_url = photo_url
    global_photo_data[key] = {'description': reply_message, 'url': photo_url}

    # Send the image with a caption
    bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption= reply_message, reply_markup= markup)
    clearphotodata()
def translate_photo(update, context, lang, str_command):
    global chatgpt
    global global_desc
    global global_url
    
    if lang  == 'EN':
        # Find the index where "translate_english_photo_" ends
        index = str_command.find("translate_english_photo_")

        # Extract the substring after "translate_english_photo_"
        Key = str_command[index + len("translate_english_photo_"):]
        global_desc = global_photo_data[Key]['description']
        global_url = global_photo_data[Key]['url']

        reply_message = chatgpt.submit('Please translate to English only and not add any commant and if content is English just return English content only,' + global_desc)
        

        
    else: 
        # Find the index where "translate_chinese_photo_" ends
        index = str_command.find("translate_chinese_photo_")

        # Extract the substring after "translate_chinese_photo_"
        Key = str_command[index + len("translate_chinese_photo_"):]
        global_desc = global_photo_data[Key]['description']
        global_url = global_photo_data[Key]['url']
        reply_message = chatgpt.submit('Please translate to Chinese only and not add any commant and if content is Chinese just return Chinese content only,' + global_desc)
        


    markup = types.InlineKeyboardMarkup(row_width=2)
    translate_english = types.InlineKeyboardButton('Translate to English'+ global_desc, callback_data= 'translate_english_photo_'+ Key)
    translate_chinese = types.InlineKeyboardButton('Translate to Chinese'+ global_desc, callback_data= 'translate_chinese_photo_'+ Key)
    markup.add(translate_english, translate_chinese)
    photo_response = requests.get(global_url)
    photo = photo_response.content
    bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption= reply_message, reply_markup= markup)
    clearphotodata()

def clearphotodata():
    count = len(global_photo_data)
    # If the count exceeds 50, remove the top 10 entries
    if count > 50:
        keys_to_remove = list(global_photo_data.keys())[:10]
        for key in keys_to_remove:
            del global_photo_data[key]


def translate_chatgpt(update, context, lang):
    global chatgpt
    global global_review
    
    if lang  == 'EN':
        reply_message = chatgpt.submit('Please translate to English only and not add any commant and if content is English just return English content only,' + global_review)
    else: 
        reply_message = chatgpt.submit('Please translate to Chinese only and not add any commant and if content is Chinese just return Chinese content only,' + global_review)
    markup = types.InlineKeyboardMarkup(row_width=2)
    translate_english = types.InlineKeyboardButton('Translate to English only and not add other command', callback_data= 'translate_english')
    translate_chinese = types.InlineKeyboardButton('Translate to Chinese only and not add other command', callback_data= 'translate_chinese')
    markup.add(translate_english, translate_chinese)
    bot.send_message(chat_id=update.effective_chat.id, text=reply_message, reply_markup=markup)

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
if __name__ == '__main__':
    main()
 