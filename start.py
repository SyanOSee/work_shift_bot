# Third-party
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Standard
import asyncio
from database import db, LogModel

# Project
from bot import bot, dispatcher
from logger import bot_logger, server_logger, database_logger
from handlers import users_router
from panel import start_panel

import config as cf

[dispatcher.include_router(router) for router in [
    users_router
]]

logging_folder = cf.BASE + '/logs'


async def start_loggers():
    logs = await db.logs.get_all()
    if logs:
        [await db.logs.delete(log=model) for model in logs]

    bot_model = LogModel()
    bot_model.file = f'http://{cf.media_server["host"]}:{cf.media_server["port"]}/get/logs/bot_log.log'
    database_model = LogModel()
    database_model.file = f'http://{cf.media_server["host"]}:{cf.media_server["port"]}/get/logs/database_log.log'
    media_model = LogModel()
    media_model.file = f'http://{cf.media_server["host"]}:{cf.media_server["port"]}/get/logs/media_log.log'

    [log.clear_log_file() for log in [bot_logger, server_logger, database_logger]]

    [await db.logs.insert(log=model) for model in [bot_model, database_model, media_model]]


async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)

    await dispatcher.start_polling(
        bot,
        allowed_updates=[
            'message', 'callback_query'
        ]  # Add needed router updates
    )


async def run_app():
    await asyncio.gather(
        start_bot(),
        start_panel()
    )


if __name__ == '__main__':
    from handlers.background import generate_report, notify_start_end_work
    scheduler = AsyncIOScheduler()
    scheduler.add_job(start_loggers)
    scheduler.add_job(run_app)
    scheduler.add_job(
        generate_report,
        trigger=CronTrigger(day_of_week=6),
        args=(True,)

    )
    scheduler.add_job(
        generate_report,
        trigger=CronTrigger(day=25),
        args=(False,)

    )
    scheduler.add_job(
        notify_start_end_work,
        'interval',
        seconds=300
    )
    scheduler.start()
    asyncio.get_event_loop().run_forever()
