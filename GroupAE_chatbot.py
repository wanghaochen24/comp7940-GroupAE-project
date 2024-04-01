from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters,
                CallbackContext)
import ssl
import random
import mysql.connector
import requests
import uuid

from pytube import YouTube
import telebot
from telebot import types
import logging
import os
from ChatGPT_HKBU import HKBU_ChatGPT


TLG_ACCESS_TOKEN = os.environ['TLG_ACCESS_TOKEN']
USER = os.environ['USER']
PSW = os.environ['PASSWORD']
HOST = os.environ['HOST']
ssl._create_default_https_context = ssl._create_stdlib_context
global_review = "" 
global_url = ""  
global_desc = "" 
global_photo_data = {'key1': {'description': 'Description 1', 'url': 'URL 1'}}


def main():

    #set bot
    global bot
    bot = telebot.TeleBot(TLG_ACCESS_TOKEN)
    updater = Updater(token=(TLG_ACCESS_TOKEN), use_context=True)
    dispatcher = updater.dispatcher

    #set chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    #commands
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("view", view_theme))
    dispatcher.add_handler(CommandHandler("review", writeReview_callback))
    dispatcher.add_handler(CallbackQueryHandler(message_handler))

    #start the bot
    updater.start_polling()
    updater.idle()


def start_command(update: Update, context: CallbackContext) -> None:

    #Send a message when command /start happends
    try:
        global bot
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
        text=' Welcome to GroupAE chatbot \n Please select the below function', reply_markup=keyboard_1)
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
        youtube_urls = [
        "https://www.youtube.com/watch?v=TwZ0J6ED_2c",
        "https://www.youtube.com/watch?v=61tFikJm0XM",
        "https://www.youtube.com/watch?v=jKHnr9n2Cw0",
	    "https://www.youtube.com/watch?v=zGmTZ6bXiSs",
        "https://www.youtube.com/watch?v=vGE-RfP6KRE",
        "https://www.youtube.com/watch?v=a3EYQARJkLk"
        ]
        random_url = random.choice(youtube_urls)
        yt = YouTube(random_url)
        video = yt.streams.filter(file_extension="mp4").get_by_resolution("360p").download("./tmp")
        bot.send_video(update.effective_chat.id, open(video, 'rb'), width=1280, height=720)


def readview_callback(update, context):
    global global_review

    #connect to the MySQL database
    cnx = mysql.connector.connect(
        user=USER,
        password=PSW,
        host=HOST,
        port=3306,
        database="chatbot",
        ssl_disabled=True,
    )
    review_data_string = ""
    cursor = cnx.cursor()
    query = "SELECT tv_show, reviewer_name, rating , review_text FROM TV_Reviews"
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        tv_show = row[0]
        reviewer_name = row[1]
        rating = row[2] 
        full_stars = int(rating)
        half_star = int((rating - full_stars) * 2)
        star_string = "\u2605" * full_stars + "\u00BD" * half_star
        review_text = row[3]
        review_data_string += (
            f"<b>{tv_show}</b>\nReviewer: {reviewer_name}\nRating: {star_string}\nReview: {review_text}\n\n"
        )

    # Close the cursor and the database connection
    cursor.close()
    cnx.close()

    #translate the reviews
    markup = types.InlineKeyboardMarkup(row_width=2)
    translate_english = types.InlineKeyboardButton('Translate to English', callback_data= 'translate_english')
    translate_chinese = types.InlineKeyboardButton('Translate to Chinese', callback_data= 'translate_chinese')
    markup.add(translate_english, translate_chinese)
    global_review= review_data_string
    bot.send_message(update.effective_chat.id,'The TV reviews as below:\n\n'+ review_data_string ,parse_mode='HTML', reply_markup=markup)


def writeReview_callback(update, context):
    try:
        result = ' '.join(context.args)
        substrings = result.split(",")
        if len(substrings) > 4:
            substrings[3] = ', '.join(substrings[3:])
            del substrings[4:]
        tvshow=substrings[0]
        reviewer=substrings[1]
        rating=substrings[2]
        review=substrings[3]

        #connect to the MySQL database
        cnx = mysql.connector.connect(
            user=USER,
            password=PSW,
            host=HOST,
            port=3306,
            database="chatbot",
            ssl_disabled=True
        )
        cursor = cnx.cursor()
        query = "INSERT INTO TV_Reviews ( tv_show, reviewer_name, rating, review_text) VALUES (%s, %s, %s, %s)"
        values = (tvshow, reviewer, rating, review)
        cursor.execute(query, values)
        cnx.commit()

        # Close the cursor and the database connection
        cursor.close()
        cnx.close()
        full_stars = int(rating)
        half_star = int((int(rating) - full_stars) * 2)
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
            photo_url = data['results'][0]['urls']['small']
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
    photo_url = data['results'][0]['urls']['small']
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
    bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption= reply_message, reply_markup= markup)
    clearphotodata()


def translate_photo(update, context, lang, str_command):
    global chatgpt
    global global_desc
    global global_url
    
    if lang  == 'EN':

        # Find the index where "translate_english_photo_" ends
        index = str_command.find("translate_english_photo_")
        Key = str_command[index + len("translate_english_photo_"):]
        global_desc = global_photo_data[Key]['description']
        global_url = global_photo_data[Key]['url']
        reply_message = chatgpt.submit('Please translate to English only and not add any commant and if content is English just return English content only,' + global_desc)     
    else: 

        # Find the index where "translate_chinese_photo_" ends
        index = str_command.find("translate_chinese_photo_")
        Key = str_command[index + len("translate_chinese_photo_"):]
        global_desc = global_photo_data[Key]['description']
        global_url = global_photo_data[Key]['url']
        reply_message = chatgpt.submit('Please translate to Chinese only and not add any commant and if content is Chinese just return Chinese content only,' + global_desc)
    markup = types.InlineKeyboardMarkup(row_width=2)
    translate_english = types.InlineKeyboardButton('Translate to English', callback_data= 'translate_english_photo_'+ Key)
    translate_chinese = types.InlineKeyboardButton('Translate to Chinese', callback_data= 'translate_chinese_photo_'+ Key)
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


def translate_chatgpt(update, context,  lang):
    global chatgpt
    global global_review

    if lang  == 'EN':
        reply_message = chatgpt.submit('Please translate to English only and not add any commant and if content is English just return English content only,' + global_review)
    else: 
        reply_message = chatgpt.submit('Please translate to Chinese only and not add any commant and if content is Chinese just return Chinese content only,' + global_review)
    markup = types.InlineKeyboardMarkup(row_width=2)
    translate_english = types.InlineKeyboardButton('Translate to English', callback_data= 'translate_english')
    translate_chinese = types.InlineKeyboardButton('Translate to Chinese', callback_data= 'translate_chinese')
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
 