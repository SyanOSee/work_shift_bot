from . import *

# __router__ !DO NOT DELETE!
facility_router = Router()


# __states__ !DO NOT DELETE!
class CreateFacilityStates(StatesGroup):
    get_title = State()
    get_city = State()
    get_position = State()
    get_access_range = State()
    get_work_range = State()


# __buttons__ !DO NOT DELETE!
async def get_decline_reply_keyboard() -> ReplyKeyboardMarkup:
    button_list = [
        [KeyboardButton(text=strs.decline_btn)],
    ]

    return ReplyKeyboardMarkup(keyboard=button_list, resize_keyboard=True, one_time_keyboard=True)


async def get_detach_worker_keyboard(worker_id: int) -> InlineKeyboardMarkup:
    button_list = [
        [InlineKeyboardButton(text='Открепить ❌', callback_data=f'facility_detach {worker_id}')]
    ]

    @facility_router.callback_query(F.data.startswith('facility_detach'))
    async def handle_detach_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_detach button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        worker_id_ = int(data[1])

        user = await db.users.get_by_id(user_id=worker_id_)
        user.current_facility_id = None
        await db.users.update(user=user)

        # Event will send this message!
        # await callback.bot.send_message(
        #     chat_id=user.id,
        #     text=strs.facility_unchoosed_by_admin
        # )

        await callback.message.delete()

        await callback.answer()

    return InlineKeyboardMarkup(inline_keyboard=button_list)


async def get_facility_location(facility_id: str) -> InlineKeyboardMarkup:
    button_list = [
        [InlineKeyboardButton(text='Местоположение 🗺️', callback_data=f'facil_get_location_btn {facility_id}')],
    ]

    @facility_router.callback_query(F.data.startswith('facil_get_location_btn'))
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


async def get_facility_info_inline_keyboard(
        attach_to: int | None,
        facility_id: str,
        back_page: int
) -> InlineKeyboardMarkup:
    if attach_to:
        button_list = [
            [InlineKeyboardButton(text='Закрепить 📌 ', callback_data=f'facility_attach_btn {attach_to} {facility_id}')],
            [InlineKeyboardButton(text='Открепить ❌ ', callback_data=f'facility_no_attach_btn {attach_to}')],
            [InlineKeyboardButton(text='Местоположение 🗺️', callback_data=f'facility_location_btn {facility_id}')],
            [InlineKeyboardButton(text='🔙 Вернуться к списку объектов', callback_data=f'facility_back_btn {attach_to}')]
        ]
    else:
        button_list = [
            [InlineKeyboardButton(text='Работники 👷🏻‍♂️ ', callback_data=f'facility_workers_btn {facility_id}')],
            [InlineKeyboardButton(text='Местоположение 🗺️', callback_data=f'facility_location_btn {facility_id}')],
            [InlineKeyboardButton(text='🔙 Вернуться к списку объектов', callback_data=f'facility_back_btn {attach_to}')]
        ]

    @facility_router.callback_query(F.data.startswith('facility_workers_btn'))
    async def handle_attach_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_info attach button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        facility_id_ = data[1]
        facility = await db.facilities.get_by_id(facility_id=facility_id_)
        workers = await db.users.get_all_with_facility_id(facility_id=facility_id_)
        if workers:
            # income, hours, rate_an_hour, facility_name
            for worker in workers:
                user_info = strs.data_update_user_info(
                    fullname=worker.fullname, post=worker.post, city=worker.city,
                    age=worker.age, phone=worker.phone, income=worker.income,
                    hours=worker.hours, rate_an_hour=worker.rate_an_hour, facility_name=facility.name
                )
                await callback.message.answer_photo(
                    photo=FSInputFile(path=cf.BASE + f'/media/{worker.id}/images/profile.png'),
                    caption=user_info,
                    reply_markup=await get_detach_worker_keyboard(worker_id=worker.id)
                )
        else:
            await callback.message.answer(
                text=strs.facility_no_workers_attached
            )
        await callback.answer()

    @facility_router.callback_query(F.data.startswith('facility_attach_btn'))
    async def handle_attach_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_info attach button callback from user {callback.message.chat.id}')
        if 'Вы закрепили данный объект!' in callback.message.text:
            await callback.answer()
            return

        data = callback.data.split()
        attach_to_ = int(data[1]) if data[1] != 'None' else None
        facility_id_ = data[2]
        user = await db.users.get_by_id(user_id=attach_to_)
        user.current_facility_id = facility_id_
        await db.users.update(user=user)
        await callback.message.edit_text(
            text=callback.message.text + '\n\n<b>Вы закрепили данный объект!</b>',
            reply_markup=callback.message.reply_markup
        )
        # Event will send this message!
        # await callback.bot.send_message(
        #     chat_id=attach_to_,
        #     text=strs.facility_choosed_by_admin
        # )

        await callback.answer()

    @facility_router.callback_query(F.data.startswith('facility_no_attach_btn'))
    async def handle_attach_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_info attach button callback from user {callback.message.chat.id}')
        if 'Вы закрепили данный объект!' not in callback.message.text:
            await callback.answer()
            return

        data = callback.data.split()
        attach_to_ = int(data[1]) if data[1] != 'None' else None
        user = await db.users.get_by_id(user_id=attach_to_)
        user.current_facility_id = None
        await db.users.update(user=user)
        await callback.message.edit_text(
            text='\n\n'.join(callback.message.text.split('\n\n')[:-1]),
            reply_markup=callback.message.reply_markup
        )

        # Event will send this message!
        # await callback.bot.send_message(
        #     chat_id=attach_to_,
        #     text=strs.facility_unchoosed_by_admin
        # )

        await callback.answer()

    @facility_router.callback_query(F.data.startswith('facility_back_btn'))
    async def handle_back_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_info back button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        attach_to_ = int(data[1]) if data[1] != 'None' else None
        user = await db.users.get_by_id(user_id=attach_to_)
        if attach_to_:
            await callback.message.edit_text(
                text=strs.facility_choose_available(
                    city=user.city, name=user.fullname
                ),
                reply_markup=await get_choose_facility_inline_keyboard(
                    attach_to=attach_to_,
                    city=user.city,
                    page=back_page
                )
            )
        else:
            await callback.message.edit_text(
                text=strs.facility_available,
                reply_markup=await get_choose_facility_inline_keyboard(
                    attach_to=attach_to_,
                    city='all',
                    page=back_page
                )
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


async def get_choose_facility_inline_keyboard(
        attach_to: int | None,
        city: str = 'Москва',
        page: int = 1
) -> InlineKeyboardMarkup:
    batch = 3

    if city == 'all':
        facilities_ = await db.facilities.get_all()
    else:
        facilities_ = await db.facilities.get_all_by_city(city=city.capitalize())

    buttons = []
    for i in range(batch * (page - 1), batch * (page - 1) + batch):
        if not facilities_ or i >= len(facilities_):
            break
        facility = facilities_[i]
        buttons.append(
            [InlineKeyboardButton(text=facility.name,
                                  callback_data=f'facility_facility_btn {attach_to} {facility.id} {page}')])

    if city == 'all':
        [buttons.append(button) for button in [
            [InlineKeyboardButton(text='◀️', callback_data=f'facility_prev_btn {attach_to} {page}'),
             InlineKeyboardButton(text='▶️', callback_data=f'facility_next_btn {attach_to} {page}')],
            [InlineKeyboardButton(text='➕ Добавить новый объект (только администраторы)',
                                  callback_data=f'facility_new_btn')],
        ]]
    else:
        [buttons.append(button) for button in [
            [InlineKeyboardButton(text='◀️', callback_data=f'facility_prev_btn {attach_to} {page}'),
             InlineKeyboardButton(text='▶️', callback_data=f'facility_next_btn {attach_to} {page}')],
            [InlineKeyboardButton(text='🔙 Вернуться к пользователю',
                                  callback_data=f'facility_back_to_user {attach_to}')],
            [InlineKeyboardButton(text='➕ Добавить новый объект (только администраторы)',
                                  callback_data=f'facility_new_btn')],
        ]]

    @facility_router.callback_query(F.data.startswith('facility_facility_btn'))
    async def handle_facility_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling choose_facility facility button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        attach_to_ = int(data[1]) if data[1] != 'None' else None
        facility_id = data[2]
        page_ = int(data[3])
        facility_ = await db.facilities.get_by_id(facility_id=facility_id)
        if facility_:
            facility_info = strs.facility_info(
                name=facility_.name, city=facility_.city,
                start_time=facility_.work_start_time, end_time=facility_.work_end_time,
                dist_range=facility_.access_get_range
            )
            await callback.message.edit_text(
                text=facility_info,
                reply_markup=await get_facility_info_inline_keyboard(
                    attach_to=attach_to_,
                    back_page=page_,
                    facility_id=facility_.id
                )
            )
        else:
            await callback.message.answer(text=strs.facility_search_error)
        await callback.answer()

    @facility_router.callback_query(F.data.startswith('facility_new_btn'))
    async def handle_facility_new_btn_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_new_btn facility button callback from user {callback.message.chat.id}')
        user_ = await db.users.get_by_id(user_id=callback.message.chat.id)
        if user_ and user_.is_admin:
            await callback.message.answer(text=strs.facility_get_title, reply_markup=await get_decline_reply_keyboard())
            await state.set_state(CreateFacilityStates.get_title.state)
        else:
            await callback.message.answer(text=strs.facility_not_admin)
        await callback.answer()

    @shift_router.callback_query(F.data.startswith('facility_prev_btn'))
    async def handle_prev_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling choose_facility prev button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        attach_to_ = int(data[1]) if data[1] != 'None' else None
        page_ = int(data[2])
        user = await db.users.get_by_id(user_id=attach_to_)
        if page_ != 1:
            await callback.message.edit_reply_markup(
                reply_markup=await get_choose_facility_inline_keyboard(
                    attach_to=attach_to_,
                    city=user.city,
                    page=page_ - 1
                )
            )
        await callback.answer()

    @shift_router.callback_query(F.data.startswith('facility_next_btn'))
    async def handle_next_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling choose_facility next button callback from user {callback.message.chat.id}')
        from math import ceil
        max_pages = ceil(len(facilities_) / batch) if facilities_ else 0
        data = callback.data.split()
        attach_to_ = int(data[1]) if data[1] != 'None' else None
        page_ = int(data[2])
        user = await db.users.get_by_id(user_id=attach_to_)
        if page_ != max_pages:
            await callback.message.edit_reply_markup(
                reply_markup=await get_choose_facility_inline_keyboard(
                    attach_to=attach_to_,
                    city=user.city,
                    page=page_ + 1
                )
            )
        await callback.answer()

    @facility_router.callback_query(F.data.startswith('facility_back_to_user'))
    async def handle_back_to_user_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_back_to_user facility button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        attach_to_ = int(data[1]) if data[1] != 'None' else None
        user = await db.users.get_by_id(user_id=attach_to_)
        facility_ = await db.facilities.get_by_id(facility_id=user.current_facility_id)
        user_info = strs.data_update_user_info(
            fullname=user.fullname, post=user.post, city=user.city,
            age=user.age, phone=user.phone, income=user.income,
            hours=user.hours, rate_an_hour=user.rate_an_hour,
            facility_name=facility_.name if facility_ else 'Отсутствует'
        )

        from .registration import get_attach_facility_keyboard
        await callback.message.delete()
        await callback.message.bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=FSInputFile(path=cf.BASE + f'/media/{user.id}/images/profile.png'),
            caption=user_info,
            reply_markup=await get_attach_facility_keyboard(
                attach_user_id=attach_to_,
                city=user.city
            )
        )
        await callback.answer()

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# __chat__ !DO NOT DELETE!
@facility_router.message(CreateFacilityStates.get_title)
async def handle_get_title_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states CreateFacilityStates.get_title from user {message.chat.id}')
    title = message.text
    if title:
        await message.answer(text=strs.facility_get_city)
        await state.update_data({
            'title': title
        })
        await state.set_state(CreateFacilityStates.get_city.state)
    else:
        await message.answer(text=strs.facility_get_title_error)


@facility_router.message(CreateFacilityStates.get_city)
async def handle_get_city_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states CreateFacilityStates.get_city from user {message.chat.id}')
    city = message.text
    if city:
        await message.answer(text=strs.facility_get_geo)
        await state.update_data({
            'city': city
        })
        await state.set_state(CreateFacilityStates.get_position.state)
    else:
        await message.answer(text=strs.facility_get_city_error)


@facility_router.message(CreateFacilityStates.get_position)
async def handle_get_position_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states CreateFacilityStates.get_position from user {message.chat.id}')
    import re
    geo = message.text
    geo_coords = message.location
    if geo and re.match(r'^\d*.?\d*,? \d*.?\d*$', geo):
        await message.answer(text=strs.facility_get_access_range)
        await state.update_data({
            'geo': geo
        })
        await state.set_state(CreateFacilityStates.get_access_range.state)
    elif geo_coords:
        await message.answer(text=strs.facility_get_access_range)
        await state.update_data({
            'geo': f'{geo_coords.latitude}, {geo_coords.longitude}'
        })
        await state.set_state(CreateFacilityStates.get_access_range.state)
    else:
        await message.answer(text=strs.facility_get_geo_error)


@facility_router.message(CreateFacilityStates.get_access_range)
async def handle_get_access_range_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states CreateFacilityStates.get_access_range from user {message.chat.id}')
    range_ = message.text
    if range_ and range_.isdigit():
        range_ = int(range_)
        if 0 < range_ <= 2000:
            await message.answer(text=strs.facility_get_work_range)
            await state.update_data({
                'access_range': range_
            })
            await state.set_state(CreateFacilityStates.get_work_range.state)
        else:
            await message.answer(text=strs.facility_get_access_range_error)
    else:
        await message.answer(text=strs.facility_get_access_range_error)


@facility_router.message(CreateFacilityStates.get_work_range)
async def handle_get_work_range_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states CreateFacilityStates.get_work_range from user {message.chat.id}')
    import re
    from datetime import datetime
    from uuid import uuid4

    work_range = message.text
    match = re.match(r'(\d{1,2}:\d{2}) *- *(\d{1,2}:\d{2})', work_range if work_range else 'aa:aa')
    if match:
        start_time_str, end_time_str = match.groups()
        start_hour, start_minute = [int(item) for item in start_time_str.split(':')]
        end_hour, end_minute = [int(item) for item in end_time_str.split(':')]
        if not (0 <= start_hour < 24) and not (0 <= start_minute < 60):
            await message.answer(text=strs.facility_get_work_range_error)
            return
        elif not (0 <= end_hour < 24) and not (0 <= end_minute < 60):
            await message.answer(text=strs.facility_get_work_range_error)
            return
        start_time_obj = datetime.strptime(start_time_str.strip(), "%H:%M").time()
        end_time_obj = datetime.strptime(end_time_str.strip(), "%H:%M").time()

        data = await state.get_data()
        facility_id = str(uuid4())[:10]
        facility = FacilityModel()
        facility.id = facility_id
        facility.name = data.get('title')
        facility.city = data.get('city').lower().capitalize()
        facility.geo = data.get('geo')
        facility.access_get_range = data.get('access_range')
        facility.work_start_time = start_time_obj,
        facility.work_end_time = end_time_obj
        await db.facilities.insert(facility=facility)
        await message.answer(text=strs.facility_created, reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer(text=strs.facility_get_work_range_error)


@facility_router.message(Private(), Command('facility'))
async def handle_my_facilities_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /facility from user {message.chat.id}')
    user = await db.users.get_by_id(user_id=message.chat.id)
    if user.current_facility_id:
        facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)
        if facility:
            facility_info = strs.facility_info(
                name=facility.name, city=facility.city.capitalize(),
                start_time=facility.work_start_time, end_time=facility.work_end_time,
                dist_range=facility.access_get_range
            )
            await message.answer(
                text=facility_info,
                reply_markup=await get_facility_location(facility_id=facility.id)
            )
            return

    await message.answer(text=strs.facility_not_available)


@facility_router.message(Private(), Command('facilities'), Admin())
async def handle_facilities_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /facilities from user {message.chat.id}')
    await message.answer(
        text=strs.facility_available,
        reply_markup=await get_choose_facility_inline_keyboard(
            attach_to=None,
            city='all'
        )
    )
