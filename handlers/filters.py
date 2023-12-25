# Third-party
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums.chat_type import ChatType

# Project
from database import db


class Admin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = await db.users.get_by_id(user_id=message.from_user.id)
        if user and user.is_admin:
            return True
        return False


class Private(BaseFilter):
    def __init__(self):
        self.chat_type = ChatType.PRIVATE.value

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
