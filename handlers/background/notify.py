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
                facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)
                if facility:
                    if current_time.hour == (facility.work_start_time.hour - 1) and not user.is_start_shift_notified:
                        await bot.send_message(chat_id=user.id, text=strs.notify_start_shift)
                        user.is_start_shift_notified = True
                        user.is_end_shift_notified = False
                        await db.users.update(user=user)
                    elif current_time.hour == (facility.work_end_time.hour - 1) and not user.is_end_shift_notified:
                        await bot.send_message(chat_id=user.id, text=strs.notify_end_shift)
                        user.is_start_shift_notified = False
                        user.is_end_shift_notified = True
                        await db.users.update(user=user)