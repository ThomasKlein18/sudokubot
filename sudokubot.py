#!/usr/bin/env python
# -*- coding: utf-8 -*-


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
#import tensorflow as tf 
import re
import numpy as np
from functools import wraps
from telegram import ChatAction

from sudoku_solve import solve_dancinglinks, print_sudoku
from sudoku_vision import parse_photo

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# ========== decorators ========== #

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update = args
            bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(bot, update, **kwargs)
        return command_func
    
    return decorator

send_typing_action = send_action(ChatAction.TYPING)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Sudokubot reporting for duty!')

def help(bot, update):
    """Display options when the command /help is issued."""
    update.message.reply_text("Send me pictures of your Sudokus, and I will solve them for you :)")


@send_typing_action
def echo(bot, update):
    if( len(update.message.photo) > 0):
        # store the picture
        bot.get_file(update.message.photo[-1]).download("sudoku.jpg")
        # read it in as photo I can work with
        img = plt.imread("sudoku.jpg")
        # transform picture to np.array
        sudoku = parse_photo(img)
        # solve sudoku
        solved = solve_dancinglinks(sudoku)
        # print to command line
        print_sudoku(solved)
        # 


    update.message.reply_text(solved)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(open("access_token.txt", 'r').read())
    

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    master_filter = Filters.user(username=["@Thomas_Klein"])

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start, master_filter))
    dp.add_handler(CommandHandler("help", help, master_filter))

    # on noncommand i.e message - echo the message on Telegram
    main_handler = MessageHandler(Filters.photo, echo, master_filter)
    dp.add_handler(main_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()