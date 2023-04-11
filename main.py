import time
from datetime import date, datetime
import logging
import random
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from dotenv import dotenv_values

BOT_TOKEN = dotenv_values(".env")['BOT_TOKEN']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

start_keyboard = [['/dice', '/timer']]
start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=False)

roll_keyboard = [['/roll 1x6', '/roll 2x6', '/roll 1x20', '/stop']]
roll_markup = ReplyKeyboardMarkup(roll_keyboard, one_time_keyboard=False)

timer_keyboard = [['/set_timer 30', '/set_timer 60', '/set_timer 300', '/stop']]
timer_markup = ReplyKeyboardMarkup(timer_keyboard, one_time_keyboard=False)


close_keyboard = [['/close']]
close_markup = ReplyKeyboardMarkup(close_keyboard, one_time_keyboard=False)


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


async def set_timer_game(update, context):
    chat_id = update.effective_message.chat_id
    seconds = int(context.args[0])
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(end, seconds, chat_id=chat_id, name=str(chat_id), data=seconds)
    if seconds < 60:
        text = f'засёк {seconds} секунд'
    else:
        text = f'засёк {seconds // 60} минут'
    if job_removed:
        text += 'старый таймер сброшен'
    await update.effective_message.reply_text(text)


async def roll(update, context):
    dice_roll = context.args[0]
    if dice_roll == '1x6':
        text = f'выпало {random.randint(1, 7)}'
    elif dice_roll == '2x6':
        text = f'на первом кубике выпало {random.randint(1, 7)}, на втором - {random.randint(1, 7)}'
    else:
        text = f'выпало {random.randint(1, 21)}'
    await update.effective_message.reply_text(text)


async def end(context):
    if context.job.data < 60:
        time_text = "30 секунд истекло"
    else:
        time_text = f"{context.job.data // 60} минут истекло"
    await context.bot.send_message(context.job.chat_id, text=time_text)


async def close(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'таймер отменен' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


async def start(update, context):
    await update.message.reply_text(
        "Привет. Я помощник для настольных игр. Выберите желаемое действие.", reply_markup=start_markup)
    if update.message.text == '/timer':
        return 1
    else:
        return 3


async def dice(update, context):
    await update.message.reply_text(f"Выберите, как будете кидать кубик", reply_markup=roll_markup)
    return 4


async def timer(update, context):
    weather = update.message.text
    logger.info(weather)
    await update.message.reply_text("Выберите срок для таймера", reply_markup=timer_markup)
    return 2


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CommandHandler("time", time_show))
    application.add_handler(CommandHandler("date", date_show))
    application.add_handler(CommandHandler("set_timer", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            3: [CommandHandler("dice", dice)],
            4: [CommandHandler("roll", roll)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    ))
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [CommandHandler("timer", timer)],
            2: [CommandHandler("set_timer_game", set_timer_game)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    ))
    application.run_polling()


if __name__ == '__main__':
    main()