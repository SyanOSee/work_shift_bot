# Third-party
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Standard
import asyncio
from database import db, connect_events, LogModel

# Project
from bot import bot, dispatcher
from logger import bot_logger, server_logger, database_logger, background_logger
from handlers import users_router
from server import start_panel

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
    bot_model.file = f'http://{cf.panel_server["host"]}:{cf.panel_server["port"]}/get/logs/bot_log.log'
    database_model = LogModel()
    database_model.file = f'http://{cf.panel_server["host"]}:{cf.panel_server["port"]}/get/logs/database_log.log'
    server_model = LogModel()
    server_model.file = f'http://{cf.panel_server["host"]}:{cf.panel_server["port"]}/get/logs/server_log.log'
    background_model = LogModel()
    background_model.file = f'http://{cf.panel_server["host"]}:{cf.panel_server["port"]}/get/logs/background_log.log'

    [log.clear_log_file() for log in [bot_logger, server_logger, database_logger, background_logger]]

    [await db.logs.insert(log=model) for model in [bot_model, database_model, server_model, background_model]]


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
        connect_events(),
        start_bot(),
        start_panel()
    )


if __name__ == '__main__':
    import handlers.background.reports as reports
    import handlers.background as back
    scheduler = AsyncIOScheduler()
    scheduler.add_job(start_loggers)
    scheduler.add_job(run_app)
    scheduler.add_job(
        reports.generate_week_report,
        trigger=CronTrigger(day_of_week=6),
    )
    scheduler.add_job(
        reports.generate_month_report,
        trigger=CronTrigger(day=25),
    )
    scheduler.add_job(
        back.notify_start_end_work,
        'interval',
        minutes=5
    )
    scheduler.add_job(
        back.check_notification,
        'interval',
        seconds=10
    )
    scheduler.add_job(
        back.clear_questions,
        'interval',
        days=1
    )
    scheduler.start()
    asyncio.get_event_loop().run_forever()
