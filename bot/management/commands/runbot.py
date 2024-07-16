# bot/management/commands/runbot.py

from django.core.management.base import BaseCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import logging
from bot.views import start, echo, handle_contact, command_not_found, button_callback


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **kwargs):
        TOKEN = '7311771640:AAH2bPWAjcU9sS-4Emv7ylQBWjKPcWucc7Q'

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        logger = logging.getLogger(__name__)

        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
        application.add_handler(MessageHandler(filters.COMMAND, command_not_found))
        application.add_handler(CallbackQueryHandler(button_callback))

        application.run_polling()
