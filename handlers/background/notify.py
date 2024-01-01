# Project
from database import db
from bot import bot

# Standard
from datetime import datetime, timezone, timedelta
from resources import strs


async def notify_start_end_work():
    users = await db.users.get_all()
    current_time = datetime.now(timezone(timedelta(hours=3)))
    if users:
        for user in users:
            if user.current_facility_id:
                shifts = await db.users.get_all_shifts(user_id=user.id)
                last_shift = None
                if shifts:
                    last_shift = shifts[-1]

                facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)
                if facility:
                    if last_shift.end_time and current_time.hour == (facility.work_start_time.hour - 1):
                        await bot.send_message(chat_id=user.id, text=strs.notify_start_shift)
                    elif not last_shift.end_time and current_time.hour == (facility.work_end_time.hour - 1):
                        await bot.send_message(chat_id=user.id, text=strs.notify_end_shift)
