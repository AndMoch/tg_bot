import time
from datetime import date, datetime
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from dotenv import dotenv_values

BOT_TOKEN = dotenv_values(".env")['BOT_TOKEN']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def echo(update, context):
    await update.message.reply_text(f"Я получил сообщение {update.message.text}")


async def time_show(update, context):
    f = "%H:%M:%S"
    await update.message.reply_text(f"{time.strftime(f, time.localtime())}")


async def date_show(update, context):
    f = "%Y.%m.%d"
    await update.message.reply_text(f"{datetime.strftime(date.today(), f)}")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    application.add_handler(echo_handler)
    time_handler = CommandHandler("time", time_show)
    application.add_handler(time_handler)
    date_handler = CommandHandler("date", date_show)
    application.add_handler(date_handler)
    application.run_polling()


if __name__ == '__main__':
    main()