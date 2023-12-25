from . import *

# __router__ !DO NOT DELETE!
facility_router = Router()


# __states__ !DO NOT DELETE!


# __buttons__ !DO NOT DELETE!
async def get_facility_info_inline_keyboard(facility_id: str, back_page: int) -> InlineKeyboardMarkup:
    button_list = [
        [InlineKeyboardButton(text='Закрепить 📌 ', callback_data=f'facility_attach_btn {facility_id}')],
        [InlineKeyboardButton(text='Местоположение 🗺️', callback_data=f'facility_location_btn {facility_id}')],
        [InlineKeyboardButton(text='🔙 Вернуться к списку объектов', callback_data='facility_back_btn')]
    ]

    @facility_router.callback_query(F.data.startswith('facility_attach_btn'))
    async def handle_attach_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_info attach button callback from user {callback.message.chat.id}')
        if 'Вы закрепили данный объект!' in callback.message.text:
            await callback.answer()
            return

        data = callback.data.split()
        facility_id_ = data[1]
        user = await db.users.get_by_id(user_id=callback.message.chat.id)
        user.current_facility_id = facility_id_
        await db.users.update(user=user)
        await callback.message.edit_text(
            text=callback.message.text + '\n\n<b>Вы закрепили данный объект!</b>',
            reply_markup=callback.message.reply_markup
        )
        await callback.answer()

    @facility_router.callback_query(F.data.startswith('facility_back_btn'))
    async def handle_back_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_info back button callback from user {callback.message.chat.id}')
        await callback.message.edit_text(
            text=strs.facility_choose_available,
            reply_markup=await get_choose_facility_inline_keyboard(user_id=callback.message.chat.id, page=back_page)
        )
        await callback.answer()

    @facility_router.callback_query(F.data.startswith('facility_location_btn'))
    async def handle_location_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_info location button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        facility_id_ = data[1]
        facility = await db.facilities.get_by_id(facility_id=facility_id_)
        if facility:
            latitude, longitude = facility.geo.replace(',', '').split()
            try:
                await callback.bot.send_location(
                    chat_id=callback.message.chat.id,
                    latitude=float(latitude),
                    longitude=float(longitude)
                )
            except Exception as e:
                bot_logger.error(e)
                bot_logger.warning('Can not send location to user!')
        await callback.answer()

    return InlineKeyboardMarkup(inline_keyboard=button_list)


async def get_choose_facility_inline_keyboard(user_id: int, page: int = 1) -> InlineKeyboardMarkup:
    batch = 3

    user = await db.users.get_by_id(user_id=user_id)
    facilities_ = await db.facilities.get_all_by_city(city=user.city.capitalize() if user else 'Москва')

    buttons = []
    for i in range(batch * (page - 1), batch * (page - 1) + batch):
        if not facilities_ or i >= len(facilities_):
            break
        facility = facilities_[i]
        buttons.append(
            [InlineKeyboardButton(text=facility.name, callback_data=f'facility_facility_btn {facility.id} {page}')])

    [buttons.append(button) for button in [
        [InlineKeyboardButton(text='◀️', callback_data=f'facility_prev_btn {page}'),
         InlineKeyboardButton(text='▶️', callback_data=f'facility_next_btn {page}')],
        [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='facility_back_to_menu')],
    ]]

    @facility_router.callback_query(F.data.startswith('facility_facility_btn'))
    async def handle_facility_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling choose_facility facility button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        facility_id = data[1]
        page_ = int(data[2])
        facility_ = await db.facilities.get_by_id(facility_id=facility_id)
        if facility_:
            facility_info = strs.facility_info(
                name=facility_.name, city=facility_.city,
                start_time=facility_.work_start_time, end_time=facility_.work_end_time
            )
            await callback.message.edit_text(
                text=facility_info,
                reply_markup=await get_facility_info_inline_keyboard(back_page=page_, facility_id=facility_.id)
            )
        else:
            await callback.message.answer(text=strs.facility_search_error)
        await callback.answer()

    @shift_router.callback_query(F.data.startswith('facility_prev_btn'))
    async def handle_prev_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling choose_facility prev button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        page_ = int(data[1])
        if page_ != 1:
            await callback.message.edit_reply_markup(
                reply_markup=await get_choose_facility_inline_keyboard(user_id=user_id, page=page_ - 1)
            )
        await callback.answer()

    @shift_router.callback_query(F.data.startswith('facility_next_btn'))
    async def handle_next_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling choose_facility next button callback from user {callback.message.chat.id}')
        from math import ceil
        max_pages = ceil(len(facilities_) / batch) if facilities_ else 0
        data = callback.data.split()
        page_ = int(data[1])
        if page_ != max_pages:
            await callback.message.edit_reply_markup(
                reply_markup=await get_choose_facility_inline_keyboard(user_id=user_id, page=page_ + 1)
            )
        await callback.answer()

    @facility_router.callback_query(F.data.startswith('facility_back_to_menu'))
    async def handle_facility_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_back_to_menu facility button callback from user {callback.message.chat.id}')
        from .general import get_menu_inline_keyboard
        await callback.message.edit_text(text=strs.menu, reply_markup=await get_menu_inline_keyboard())
        await callback.answer()

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# __chat__ !DO NOT DELETE!
@facility_router.message(Private(), Command('facilities'))
async def handle_my_facilities_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /facilities from user {message.chat.id}')
    user = await db.users.get_by_id(user_id=message.chat.id)
    if user and user.current_facility_id:
        facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)
        if facility:
            facility_info = strs.facility_info(
                name=facility.name, city=facility.city.capitalize(),
                start_time=facility.work_start_time, end_time=facility.work_end_time
            )
            await message.answer(
                text=facility_info,
                reply_markup=await get_facility_info_inline_keyboard(facility_id=facility.id, back_page=1)
            )
            return

    await message.answer(
        text=strs.facility_choose_available,
        reply_markup=await get_choose_facility_inline_keyboard(
            user_id=message.chat.id,
        )
    )
