from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton

import configparser #I keep using for config for non-sensitive information for easier udpate.
import os
from ChatGPT_HKBU import HKBU_ChatGPT
import logging
from CryptoPrice import getCoinPrice, getCoinDetails
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Increment
from flask import Flask, request


updater = Updater(token=(os.environ['TELEGRAM_ACCESS_TOKEN']), use_context=True)
dispatcher = updater.dispatcher
# Flask app instance
app = Flask(__name__)



#handle webhook updates
@app.route('/7940project794023470941', methods=['POST'])
def webhook_handler():

    # Retrieve the message in JSON and then transform it to Telegram object
    update = Update.de_json(request.get_json(force=True), updater.bot)
    
    # Process the update
    dispatcher.process_update(update)
    return 'ok', 200


def main():

# Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')

    #updater = Updater(token=(os.environ['TELEGRAM_ACCESS_TOKEN']), use_context=True)
    #dispatcher = updater.dispatcher

    
# You can set this logging module, so you will know when and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  level=logging.INFO)


    # dispatcher for chatgpt

    global chatgpt
    chatgpt = HKBU_ChatGPT(os.environ['CHATGPT_ACCESS_TOKEN'], config)
              
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

# on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", help_command))
#   add custom button
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('price', price))
    dispatcher.add_handler(CommandHandler('addcoin', addcoin))
    dispatcher.add_handler(CommandHandler('removecoin', removecoin))
    dispatcher.add_handler(CommandHandler('hotestcoin', hotestcoin))
    dispatcher.add_handler(CallbackQueryHandler(button))

# To start the bot:

    PORT = int(os.environ.get('PORT', 8443))
    WEBHOOK_URL = "https://comp7940telegramproject-53qoqwa55q-df.a.run.app/7940project794023470941"

    #updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=os.environ['TELEGRAM_ACCESS_TOKEN'])
    #updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=os.environ['TELEGRAM_ACCESS_TOKEN'],webhook_url = "https://comp7940telegramproject-53qoqwa55q-df.a.run.app/" + os.environ['TELEGRAM_ACCESS_TOKEN'])
    #updater.bot.setWebhook("https://comp7940telegramproject-53qoqwa55q-df.a.run.app/7940project794023470941" + "/" + os.environ['TELEGRAM_ACCESS_TOKEN'])
    updater.bot.set_webhook(WEBHOOK_URL)
    
    #updater.start_polling()
    app.run(host="0.0.0.0", port=PORT)
    #updater.idle()
    


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
                              'You can control me by sending these commands:\n'
                              '/help - list all commands\n'
                              '/price - check the current market price and get analysis from the coin list.\n'
                              '/hotestCoin - check the hostest coin by by inquiry count \n'
                              '/addcoin - add new cryptocurrency to the menu (eg. /addcoin bitcoin) \n'
                              '(Plesae check coinmarketcap.com for correct coin name before adding coin, you can try to add popular coin like dogecoin, bnb etc.) \n'
                              '/removecoin - remove cryptocurrency from the menu (eg. /removeCoin bitcoin) \n'
                              
                              )


def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


#coinList = ["bitcoin", "ethereum", "tether", "solana"]

def start(update: Update, context: CallbackContext) -> None:
#InlineKeyboardButton("Check Price", callback_data= context.bot.send_message(chat_id=update.effective_chat.id, text="price hahaha")
    
    #reply_markup = InlineKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    update.message.reply_text('Welcome to the Crypto Price Analysis Bot!\n'
                              'Harness the power of advanced analytics to stay ahead in the cryptocurrency markets.\n'
                              'I provide real-time price analysis, trend forecasts, and market insights.\n\n'
                              'You can control me by sending these commands:\n'
                              '/help - list all commands\n'
                              '/price - check the current market price and get analysis from the coin list.\n'
                              '/hotestCoin - check the hostest coin by by inquiry count \n'
                              '/addcoin - add new cryptocurrency to the menu (eg. /addcoin bitcoin) \n'
                              '(Plesae check coinmarketcap.com for correct coin name before adding coin, you can try to add popular coin like dogecoin, bnb etc.) \n'
                              '/removecoin - remove cryptocurrency from the menu (eg. /removeCoin bitcoin) \n'
                              )

coin_list = []
coin_name = []


# for firebase service


#cred_json = json.dumps(cred_dict)
#cred = credentials.Certificate("./project-of-telegrambot2-firebase-adminsdk-v6bry-e5a35a2ffe.json")
cred = credentials.Certificate("/firebase/google_firebase_for_telegram_chatbot")
#cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)
# Initialize Firestore instance
db = firestore.client()
collection_ref = db.collection("coinList")


def getCoinList():    

    global coin_list 
    global coin_name
    coin_list = []
    coin_name = []
    
    docs = collection_ref.stream()            
    for doc in docs:
        coin_list.append(doc.to_dict())
        coin_name.append(doc.to_dict()['coinName'])
        
getCoinList()

def price(update: Update, context: CallbackContext) -> None:

    getCoinList()
    keyboard = []
    for coinDict in coin_list:
        coin_name = coinDict['coinName']
        button = InlineKeyboardButton(coin_name, callback_data=coin_name.lower())
        keyboard.append([button])
    

    reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True,resize_keyboard=True)
    update.message.reply_text('Please choose a cryptocurrency to check', reply_markup=reply_markup)     


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()
    if query.data in coin_name:
        thePrice = getCoinPrice(query.data)
        query.edit_message_text(text=f"Current price of the selected cryptocurrency is: {thePrice}") 
        analysis = chatgpt.submit("Analysis this crypto: " + json.dumps(getCoinDetails(query.data)))
        counter(query.data)
        getCoinList()
        context.bot.send_message(chat_id=update.effective_chat.id, text=analysis)

def counter(field_value):
    global db
    # Query the collection using positional arguments for the 'where' method
    query = db.collection("coinList").where('coinName', '==', field_value)
    # Get the documents that match the query
    docs = query.stream()
    
    # Update each document
    for doc in docs:
        doc_ref = doc.reference
        doc_ref.update({"count": Increment(1)})

def addcoin(update: Update, context: CallbackContext) -> None:
    global collection_ref
    collection_ref.add({"coinName": context.args[0], "count": 0})
    context.bot.send_message(chat_id=update.effective_chat.id, text= "Added a new coin: " + context.args[0])
        
def removecoin(update: Update, context: CallbackContext) -> None:
    
    # Query the collection using positional arguments for the 'where' method
    query = db.collection("coinList").where('coinName', '==', context.args[0])
    # Get the documents that match the query
    docs = query.stream()
    
    # Delete each document
    for doc in docs:
        doc.reference.delete()
    context.bot.send_message(chat_id=update.effective_chat.id, text=  context.args[0] + " has been removed." )

def hotestcoin(update: Update, context: CallbackContext) -> None:
    global coin_list
    coin_with_highest_count = max(coin_list, key=lambda x: x['count'])
    context.bot.send_message(chat_id=update.effective_chat.id, text= \
                             f"The coin with the highest inquiry count is {coin_with_highest_count['coinName']} with a count of {coin_with_highest_count['count']}.")


if __name__ == '__main__':
    
    main()

