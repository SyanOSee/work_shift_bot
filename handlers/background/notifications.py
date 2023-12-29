# Project
import config as cf
from bot import bot
from resources import strs


async def _notify_facility_changed(to_id: int, value: str):
    if value == 'None':
        await bot.send_message(
            chat_id=int(to_id),
            text=strs.facility_unchoosed_by_admin
        )
    else:
        await bot.send_message(
            chat_id=int(to_id),
            text=strs.facility_choosed_by_admin
        )


async def _notify_admin_changed(to_id: int, value: str):
    if value == 'True':
        await bot.send_message(
            chat_id=int(to_id),
            text=strs.you_admin_now
        )
    else:
        await bot.send_message(
            chat_id=int(to_id),
            text=strs.you_not_admin_now
        )


async def _notify_post_changed(to_id: int, value: str):
    if value == 'None':
        await bot.send_message(
            chat_id=int(to_id),
            text=strs.no_post_now
        )
    else:
        await bot.send_message(
            chat_id=int(to_id),
            text=strs.new_post_now(post=value)
        )


async def check_notification():
    with open(cf.BASE + '/database/notifications.txt', 'r', encoding='utf-16') as f:
        changes = f.readlines()
    to_delete = []
    for change in changes:
        change_id, to_id, variable_name, value = change.split()
        match variable_name:
            case 'facility_id':
                await _notify_facility_changed(to_id=to_id, value=value)
                to_delete.append(change_id)
            case 'is_admin':
                await _notify_admin_changed(to_id=to_id, value=value)
                to_delete.append(change_id)
            case 'post':
                await _notify_post_changed(to_id=to_id, value=value.replace('__', ' '))
                to_delete.append(change_id)
            case _:
                pass

    with open(cf.BASE + '/database/notifications.txt', 'r', encoding='utf-16') as f:
        updated_lines = f.readlines()
    new_lines = []
    for line in updated_lines:
        if not any(line.startswith(prefix) for prefix in to_delete):
            new_lines.append(line)
    with open(cf.BASE + '/database/notifications.txt', 'w', encoding='utf-16') as f:
        f.writelines(new_lines)
