from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger  # Импортируем CronTrigger
from datetime import datetime
import random
import pytz
from compliments import compliments  # Импортируем список комплиментов

# Словарь для отслеживания состояний пользователей
user_states = {}

# Словарь для хранения отправленных комплиментов
sent_compliments = {}

# Обработчик планировщика
scheduler = BackgroundScheduler()

# Функция для отправки комплимента в 9 утра по Москве
async def send_daily_compliment(application: Application):
    now = datetime.now(pytz.timezone('Europe/Moscow'))
    for user_id, compliments_sent in sent_compliments.items():
        unused_compliments = [comp for comp in compliments if comp not in compliments_sent]
        if unused_compliments:
            compliment = random.choice(unused_compliments)
            compliments_sent.append(compliment)
            await application.bot.send_message(user_id, compliment)

# Команда /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_states[user_id] = 'started'  # Помечаем, что пользователь запустил бота
    sent_compliments[user_id] = []  # Инициализируем список отправленных комплиментов
    await update.message.reply_text("Комплименты играют важную роль в интимных отношениях, влияя на уверенность и эмоциональное состояние партнера, включая влияние на сексуальное самочувствие. Исследования показывают, что комплименты могут напрямую влиять на сексуальную активность и удовлетворенность. Например, исследование, проведенное в 2019 году, показало, что 68% женщин чувствуют себя более привлекательными и уверенными в постели, когда получают комплименты от партнера о своей внешности и сексуальных качествах.")
    await update.message.reply_text("Другие исследования подтверждают, что комплименты, касающиеся не только внешности, но и личных качеств или сексуальных достижений, могут улучшить качество интимной жизни. В исследовании 2020 года, опубликованном в журнале The Journal of Sex Research, более 75% женщин заявили, что комплименты, выражающие признание и уважение, повышают их сексуальное удовлетворение, создавая атмосферу доверия и эмоциональной близости. Это способствует улучшению сексуальных отношений и снижению стресса, что в свою очередь положительно влияет на сексуальную жизнь.")
    await update.message.reply_text("Давай начнем с первого комплимента")
    await new_compliment(update, context)  # Сразу отправляем первый комплимент

# Команда /stop
async def stop(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_states:
        user_states[user_id] = 'stopped'  # Помечаем, что пользователь остановил бота
        await update.message.reply_text("Бот остановлен. Напиши /start, чтобы снова запустить меня.")
    else:
        await update.message.reply_text("Ты ещё не запустил меня. Напиши /start, чтобы начать.")

# Команда /new (выдача комплимента)
async def new_compliment(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in user_states and user_states[user_id] == 'started':
        # Находим комплименты, которые еще не отправлялись
        unused_compliments = [comp for comp in compliments if comp not in sent_compliments[user_id]]
        
        if unused_compliments:
            # Выбираем случайный комплимент из неотправленных
            compliment = random.choice(unused_compliments)
            # Добавляем его в список отправленных
            sent_compliments[user_id].append(compliment)
            await update.message.reply_text(compliment)
            # Скажем, что следующий комплимент будет в 9 утра по Москве
            await update.message.reply_text("Следующий комплимент я отправлю тебе завтра в 9 утра по Москве, stay tuned! Напиши «/more», если не хочешь ждать")
        else:
            # Если все комплименты были отправлены, сбрасываем список
            sent_compliments[user_id] = []
            await update.message.reply_text("Ты уже получил все комплименты! Сбросим их и начнем заново.")
    else:
        await update.message.reply_text("Сначала напиши /start, чтобы запустить бота.")

# Основная функция для запуска бота
def main():
    token = '8129280242:AAEqpsSd4ngdG5yYRqcJIde2k2VivfirMEw'  # Вставьте сюда свой токен, полученный от BotFather
    application = Application.builder().token(token).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("more", new_compliment))

    # Запуск планировщика для отправки комплиментов в 9 утра по Москве
    # Используем CronTrigger для выполнения задачи ежедневно в 9:00
    scheduler.add_job(lambda: send_daily_compliment(application), CronTrigger(hour=9, minute=0, second=0, timezone='Europe/Moscow'))
    scheduler.start()

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
