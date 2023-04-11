import subprocess
import os
import re
import logging

import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, Dispatcher
import telebot

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define conversation states
CODEWORD = 123

# Define the cancel function
def cancel(update, context):
    context.user_data.clear()
    update.message.reply_text('Операция отменена.')
    return ConversationHandler.END

# Define the start function
def start(update, context):
    update.message.reply_text('Добро пожаловать в бота настройки VPN! Пожалуйста, введите кодовое слово.')
    return CODEWORD

# Define the codeword function
def codeword(update, context):
    codeword = update.message.text.strip()
    if codeword == 'mycodeword':
        # Generate a WireGuard VPN configuration file
        private_key = subprocess.run('wg genkey', shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
        public_key = subprocess.run(f'echo {private_key} | wg pubkey', shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
        # config = f'[Interface]\nPrivateKey = {private_key}\nAddress = 10.0.0.1/24\nListenPort = 51820\n\n[Peer]\nPublicKey = <server_public_key>\nAllowedIPs = 0.0.0.0/0\nEndpoint = <server_ip>:<server_port>'
        config = f'[Interface]\nPrivateKey = CHLucHaWqsPhRPPVZHXhAV0N4RG7qLh3DZsP+ASH+1Q=\nAddress = 10.0.0.1/24\nDNS = 1.1.1.1\n\n[Peer]\nPublicKey = kr3FmBisjqr5FEihvg/q98tK1biCXxHZT8EYTr/rvC0=\nPresharedKey = PdKoxwLDAz1m5em0a77Hj5wI5Jw5OBE2n2AWA+VrVGQ=\nAllowedIPs = 0.0.0.0/0, ::/0\nPersistentKeepalive = 0\nEndpoint = 185.125.202.254:51820'
        with open(f'{codeword}.conf', 'w') as f:
            f.write(config)
        # Send the configuration file and its content to the user
        with open(f'{codeword}.conf', 'r') as f:
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(f'{codeword}.conf', 'rb'))
            context.bot.send_message(chat_id=update.effective_chat.id, text=f.read())
        # Delete the configuration file
        os.remove(f'{codeword}.conf')
        update.message.reply_text('Конфигурация VPN отправлена. Благодарим вас за использование бота для настройки VPN!')
    else:
        update.message.reply_text('Неверное кодовое слово. Повторите попытку или введите /cancel для выхода.')
        return CODEWORD


# Define the main function
def main():
    # Set up the Telegram Bot API
    updater = Updater('6225150065:AAF5wn2irBUOsBeIvKnVHz3aVyvXxDDrtNQ', use_context=True)
    dispatcher = telegram.ext.Dispatcher

    # Set up the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CODEWORD: [MessageHandler(Filters.text & ~Filters.command, codeword)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add handlers to the bot
    dispatcher.add_handler(conv_handler)

    # Start the bot
    updater.start_polling()

    # Run the bot until it is stopped
    updater.idle()

if __name__ == '__main__':
    main()
