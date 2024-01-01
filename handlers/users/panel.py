from . import *

# __router__ !DO NOT DELETE!
panel_router = Router()


# __states__ !DO NOT DELETE!
class PanelInfoStates(StatesGroup):
    data_collecting = State()


# __buttons__ !DO NOT DELETE!
async def get_export_inline_keyboard() -> InlineKeyboardMarkup:
    button_list = [
        [InlineKeyboardButton(text='Недельный отчет 📅', url=cf.reports['weekly'])],
        [InlineKeyboardButton(text='Месячный отчет 🗓️', url=cf.reports['monthly'])],
        [InlineKeyboardButton(text='Отчет всех пользователей 👷🏻‍♂️', url=cf.reports['all_users'])],
    ]

    return InlineKeyboardMarkup(inline_keyboard=button_list)


async def get_decline_reply_keyboard() -> ReplyKeyboardMarkup:
    button_list = [
        [KeyboardButton(text=strs.decline_btn)],
    ]

    return ReplyKeyboardMarkup(keyboard=button_list, resize_keyboard=True, one_time_keyboard=True)


# __chat__ !DO NOT DELETE!
@panel_router.message(Private(), Command('server'), Admin())
async def handle_get_admin_panel_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling /admin_panel command from user {message.chat.id}')
    await message.answer(text=strs.panel_ask_info_msg, reply_markup=await get_decline_reply_keyboard())
    await state.set_state(PanelInfoStates.data_collecting.state)


@panel_router.message(Private(), PanelInfoStates.data_collecting)
async def handle_panel_info_collecting_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling server info collecting state from user {message.chat.id}')
    info = message.text
    if ' ' not in info:
        await message.answer(text=strs.panel_invalid_input_msg)
    else:
        login, password = info.split(maxsplit=1)
        if login == cf.database['user'] and password == cf.database['password']:
            await message.answer(
                text=f'<b>Ссылка на панель: {cf.panel_server["url"]}/admin</b>',
                reply_markup=await get_export_inline_keyboard()
            )
            await state.clear()
        else:
            await message.answer(text=strs.panel_invalid_login_password_msg)
