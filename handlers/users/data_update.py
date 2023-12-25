from . import *

# __router__ !DO NOT DELETE!
data_update_router = Router()


# __states__ !DO NOT DELETE!
class InfoChangeStates(StatesGroup):
    get_fullname = State()
    get_city = State()
    get_age = State()
    get_phone = State()
    get_photo = State()


# __buttons__ !DO NOT DELETE!
async def get_decline_reply_keyboard() -> ReplyKeyboardMarkup:
    button_list = [
        [KeyboardButton(text=strs.decline_btn)],
    ]

    return ReplyKeyboardMarkup(keyboard=button_list, resize_keyboard=True, one_time_keyboard=True)


async def get_change_personal_data_inline_keyboard() -> InlineKeyboardMarkup:
    button_list = [
        [InlineKeyboardButton(text='ФИО 🪪', callback_data='data_update_fullname_btn')],
        [InlineKeyboardButton(text='Город проживания 🌆', callback_data='data_update_city_btn')],
        [InlineKeyboardButton(text='Возраст 📆', callback_data='data_update_age_btn')],
        [InlineKeyboardButton(text='Номер телефона 📞', callback_data='data_update_phone_btn')],
        [InlineKeyboardButton(text='Фотография профиля 📸', callback_data='data_update_photo_btn')],
        [InlineKeyboardButton(text='🔙 Вернуться в меню', callback_data='data_update_back_to_menu')],

    ]

    @data_update_router.callback_query(F.data.startswith('data_update_fullname_btn'))
    async def handle_fullname_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling change_personal_data fullname button callback from user {callback.message.chat.id}')
        await callback.message.answer(text=strs.data_update_ask_fullname,
                                      reply_markup=await get_decline_reply_keyboard())
        await state.set_state(InfoChangeStates.get_fullname.state)

        @data_update_router.message(InfoChangeStates.get_fullname)
        async def handle_get_fullname_state(message: Message, state: FSMContext):
            bot_logger.info(f'Handling states InfoChangeStates.get_fullname from user {message.from_user.id}')
            fullname = message.text
            if fullname:
                user = await db.users.get_by_id(user_id=message.from_user.id)
                if user:
                    user.fullname = fullname
                    await db.users.update(user=user)
                    await message.answer(text=strs.data_update_fullname_changed, reply_markup=ReplyKeyboardRemove())
                await state.clear()
            else:
                await message.answer(text=strs.data_update_fullname_change_error)

        await callback.answer()

    @data_update_router.callback_query(F.data.startswith('data_update_city_btn'))
    async def handle_city_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling change_personal_data city button callback from user {callback.message.chat.id}')
        await callback.message.answer(text=strs.data_update_ask_city, reply_markup=await get_decline_reply_keyboard())
        await state.set_state(InfoChangeStates.get_city.state)

        @registration_router.message(InfoChangeStates.get_city)
        async def handle_get_city_state(message: Message, state: FSMContext):
            bot_logger.info(f'Handling states InfoChangeStates.get_city from user {message.from_user.id}')
            city = message.text
            if city:
                user = await db.users.get_by_id(user_id=message.from_user.id)
                if user:
                    user.city = city
                    await db.users.update(user=user)
                    await message.answer(text=strs.data_update_city_changed, reply_markup=ReplyKeyboardRemove())
                await state.clear()
            else:
                await message.answer(text=strs.data_update_city_change_error)

        await callback.answer()

    @data_update_router.callback_query(F.data.startswith('data_update_age_btn'))
    async def handle_age_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling change_personal_data age button callback from user {callback.message.chat.id}')
        await callback.message.answer(text=strs.data_update_ask_age, reply_markup=await get_decline_reply_keyboard())
        await state.set_state(InfoChangeStates.get_age.state)

        @registration_router.message(InfoChangeStates.get_age)
        async def handle_get_age_state(message: Message, state: FSMContext):
            bot_logger.info(f'Handling states InfoChangeStates.get_age from user {message.from_user.id}')
            age = message.text
            if age and age.isdigit():
                age = int(age)

                if age <= 0 or age >= 100:
                    await message.answer(text='data_update_get_age_error')
                    return

                user = await db.users.get_by_id(user_id=message.from_user.id)
                if user:
                    user.age = age
                    await db.users.update(user=user)
                    await message.answer(text=strs.data_update_age_changed, reply_markup=ReplyKeyboardRemove())
                await state.clear()
            else:
                await message.answer(text=strs.data_update_age_change_error)

        await callback.answer()

    @data_update_router.callback_query(F.data.startswith('data_update_phone_btn'))
    async def handle_phone_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling change_personal_data phone button callback from user {callback.message.chat.id}')
        await callback.message.answer(text=strs.data_update_ask_phone, reply_markup=await get_decline_reply_keyboard())
        await state.set_state(InfoChangeStates.get_phone.state)

        @registration_router.message(InfoChangeStates.get_phone)
        async def handle_get_phone_state(message: Message, state: FSMContext):
            import re
            bot_logger.info(f'Handling states InfoChangeStates.get_phone from user {message.from_user.id}')
            phone = message.text
            phone_matcher = re.compile(r'^\+?\d{10,15}$')
            if phone and phone_matcher.match(phone):
                user = await db.users.get_by_id(user_id=message.from_user.id)
                if user:
                    user.phone = phone
                    await db.users.update(user=user)
                    await message.answer(text=strs.data_update_phone_changed, reply_markup=ReplyKeyboardRemove())
                await state.clear()
            else:
                await message.answer(text=strs.data_update_phone_change_error)

        await callback.answer()

    @data_update_router.callback_query(F.data.startswith('data_update_photo_btn'))
    async def handle_photo_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling change_personal_data photo button callback from user {callback.message.chat.id}')
        await callback.message.answer(text=strs.data_update_ask_photo, reply_markup=await get_decline_reply_keyboard())
        await state.set_state(InfoChangeStates.get_photo.state)

        @data_update_router.message(InfoChangeStates.get_photo)
        async def handle_get_photo_state(message: Message, state: FSMContext):
            bot_logger.info(f'Handling states InfoChangeStates.get_photo from user {message.from_user.id}')
            import os
            from handlers.utils import download_image
            photo = message.photo
            if photo:
                file = await message.bot.get_file(file_id=photo[-1].file_id)
                url = f'https://api.telegram.org/file/bot{cf.bot["token"]}/{file.file_path}'

                folder_path = f'media/{message.from_user.id}/images'
                if not os.path.exists(cf.BASE + '/' + folder_path):
                    os.makedirs(cf.BASE + '/' + folder_path, exist_ok=True)

                destination = f'{folder_path}/profile.png'
                is_successfully = await download_image(image_url=url, destination=destination)
                if is_successfully:
                    url = f'http://{cf.media_server["host"]}:{cf.media_server["port"]}/get/{destination}'

                user = await db.users.get_by_id(user_id=message.from_user.id)
                if user:
                    user.photo = url
                    await db.users.update(user=user)
                    await message.answer(text=strs.data_update_photo_changed, reply_markup=ReplyKeyboardRemove())
                await state.clear()
                await state.clear()
            else:
                await message.answer(text=strs.data_update_photo_change_error)

        await callback.answer()

    @data_update_router.callback_query(F.data.startswith('data_update_back_to_menu'))
    async def handle_data_update_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling facility_back_to_menu facility button callback from user {callback.message.chat.id}')
        from .general import get_menu_inline_keyboard
        if callback.message.text:
            await callback.message.edit_text(text=strs.menu, reply_markup=await get_menu_inline_keyboard())
        else:
            await callback.message.delete()
            await callback.message.answer(text=strs.menu, reply_markup=await get_menu_inline_keyboard())
        await callback.answer()

    return InlineKeyboardMarkup(inline_keyboard=button_list)


# __chat__ !DO NOT DELETE!
@data_update_router.message(Private(), Command('my_data'))
async def handle_my_data_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /my_data from user {message.chat.id}')
    user = await db.users.get_by_id(user_id=message.chat.id)
    if user:
        folder_path = f'media/{user.id}/images'
        destination = f'{cf.BASE}/{folder_path}/profile.png'
        try:
            facility = None
            if user.current_facility_id:
                facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)

            user_info = strs.data_update_user_info(
                fullname=user.fullname, post=user.post, city=user.city,
                age=user.age, phone=user.phone, income=round(user.income, 2),
                hours=round(user.hours, 2), rate_an_hour=user.rate_an_hour,
                facility_name=facility.name if facility else 'отсутствует'
            )
            await message.answer_photo(
                photo=FSInputFile(path=destination, filename='profile.png'),
                caption=user_info,
                reply_markup=await get_change_personal_data_inline_keyboard()
            )
        except Exception as e:
            bot_logger.error(f'Can not send profile image of user {message.chat.id}!')
            facility = None
            if user.current_facility_id:
                facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)

            user_info = strs.data_update_user_info(
                fullname=user.fullname, post=user.post, city=user.city,
                age=user.age, phone=user.phone, income=round(user.income, 2),
                hours=round(user.hours, 2), rate_an_hour=user.rate_an_hour,
                facility_name=facility.name if facility else 'отсутствует'
            )
            await message.answer(text=user_info, reply_markup=await get_change_personal_data_inline_keyboard())
