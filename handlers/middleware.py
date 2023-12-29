# Third-party
from aiogram.types import Message
from aiogram.dispatcher.event.bases import CancelHandler
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

# Project
from database import db
from bot import bot
from resources import strs


class AuthCheckMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user_id = data.get('event_from_user').id
        if user_id:
            user = await db.users.get_by_id(user_id=user_id)
            if not user:
                await bot.send_message(chat_id=user_id, text=strs.registration_needed)
                return CancelHandler()

        result = await handler(event, data)
        return result
