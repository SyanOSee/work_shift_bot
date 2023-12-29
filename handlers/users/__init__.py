# Third-party
import asyncio

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ErrorEvent, CallbackQuery, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton

# Project
from handlers.filters import Private, Admin
from handlers.middleware import AuthCheckMiddleware
from logger import bot_logger
from database import db, UserModel, ShiftModel, FacilityModel, QuestionModel
import config as cf
from resources import strs

# Routers
from .general import general_router
from .registration import registration_router
from .shift import shift_router
from .facilities import facility_router
from .data_update import data_update_router
from .questions import questions_router
from .panel import panel_router

users_router = Router()
routers = [
    general_router, registration_router, shift_router,
    facility_router, data_update_router, questions_router,
    panel_router
]

# Setting middleware
for router in routers:
    if router != registration_router:
        router.message.middleware(AuthCheckMiddleware())
        router.callback_query.middleware(AuthCheckMiddleware())

users_router.include_routers(*routers)


@users_router.message(F.text == strs.decline_btn)
async def handle_decline_message(message: Message, state: FSMContext):
    bot_logger.info(f'Handling decline state from user {message.from_user.id}')
    await state.clear()
    await message.answer(
        text='<b>Состояние команды сброшено!</b>\n\nВоспользуйтесь командой <i>/help</i> или <i>/menu</i> для дальнейших действий',
        reply_markup=ReplyKeyboardRemove())