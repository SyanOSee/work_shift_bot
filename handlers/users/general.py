from . import *

# __router__ !DO NOT DELETE!
general_router = Router()


# __states__ !DO NOT DELETE!


# __buttons__ !DO NOT DELETE!
async def get_menu_inline_keyboard() -> InlineKeyboardMarkup:
    button_list = [
        [InlineKeyboardButton(text='Начать смену 🟢', callback_data='start_shift_btn')],
        [InlineKeyboardButton(text='Закрыть смену ⛔', callback_data='end_shift_btn')],
        [InlineKeyboardButton(text='Объекты 🏢', callback_data='facilities_btn'),
         InlineKeyboardButton(text='Мои данные 🔎', callback_data='my_data_btn')],
        [InlineKeyboardButton(text='Помощь ❓', callback_data='help_btn')]
    ]

    @general_router.callback_query(F.data.startswith('help_btn'))
    async def handle_help_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling menu help button callback from user {callback.message.chat.id}')
        await handle_help_command(message=callback.message, state=state)
        await callback.answer()

    @general_router.callback_query(F.data.startswith('start_shift_btn'))
    async def handle_start_shift_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling menu start_shift button callback from user {callback.message.chat.id}')
        from .shift import handle_start_shift_command
        await handle_start_shift_command(message=callback.message, state=state)
        await callback.answer()

    @general_router.callback_query(F.data.startswith('end_shift_btn'))
    async def handle_end_shift_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling menu end_shift button callback from user {callback.message.chat.id}')
        from .shift import handle_end_shift_command
        await handle_end_shift_command(message=callback.message, state=state)
        await callback.answer()

    @general_router.callback_query(F.data.startswith('facilities_btn'))
    async def handle_facilities_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling menu facilities button callback from user {callback.message.chat.id}')
        from .facilities import handle_my_facilities_command
        await handle_my_facilities_command(message=callback.message, state=state)
        await callback.answer()

    @general_router.callback_query(F.data.startswith('my_data_btn'))
    async def handle_my_data_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling menu my_data button callback from user {callback.message.chat.id}')
        from .data_update import handle_my_data_command
        await handle_my_data_command(message=callback.message, state=state)
        await callback.message.delete()
        await callback.answer()

    return InlineKeyboardMarkup(inline_keyboard=button_list)


# __chat__ !DO NOT DELETE!
@general_router.message(Private(), Command('start'))
async def handle_start_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /start from user {message.from_user.id}')
    await message.answer(text=strs.welcome)
    user = await db.users.get_by_id(user_id=message.from_user.id)
    if user:
        await handle_menu_command(message=message, state=state)
        return
    else:
        await message.answer(text=strs.registration_started)
        from .registration import handle_registration_command
        await handle_registration_command(message=message, state=state)


@general_router.message(Private(), Command('menu'))
async def handle_menu_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /menu from user {message.from_user.id}')
    await message.answer(text=strs.menu, reply_markup=await get_menu_inline_keyboard())


@general_router.message(Private(), Command('help'))
async def handle_help_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /help from user {message.from_user.id}')
    await message.answer(text=strs.help)


@general_router.message(Private(), Command('unemployed'), Admin())
async def handle_unemployed_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /unemployed command from user {message.chat.id}')
    unemployed = await db.users.get_all_unemployed()
    if unemployed:
        handled = 0
        for user in unemployed:
            facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)
            if not user.is_admin:
                user_info = strs.data_update_user_info(user=user, facility_name=facility.name if facility else 'Отсутствует')
                from .registration import get_attach_facility_keyboard
                await message.answer_photo(
                    photo=FSInputFile(path=cf.BASE + f'/media/{user.id}/images/profile.png'),
                    caption=user_info,
                    reply_markup=await get_attach_facility_keyboard(
                        attach_user_id=user.id,
                        city=user.city
                    )
                )
                handled += 1
        if handled == 0:
            await message.answer(text=strs.no_unemployed)
    else:
        await message.answer(text=strs.no_unemployed)