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


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update, context):
    chat_id = update.effective_message.chat_id
    seconds = int(context.args[0])
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, seconds, chat_id=chat_id, name=str(chat_id), data=seconds)

    text = f'Вернусь через {seconds} с.!'
    if job_removed:
        text += ' Старая задача удалена.'
    await update.effective_message.reply_text(text)


async def task(context):
    await context.bot.send_message(context.job.chat_id, text=f'КУКУ! {context.job.data}c. прошли!')


async def unset(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CommandHandler("time", time_show))
    application.add_handler(CommandHandler("date", date_show))
    application.add_handler(CommandHandler("set_timer", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.run_polling()


if __name__ == '__main__':
    main()