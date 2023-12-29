from . import *

# __router__ !DO NOT DELETE!
registration_router = Router()


# __states__ !DO NOT DELETE!
class RegistrationStates(StatesGroup):
    get_fullname = State()
    get_post = State()
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


async def get_attach_facility_keyboard(attach_user_id: int, city: str) -> InlineKeyboardMarkup:
    button_list = [
        [InlineKeyboardButton(text='Закрепить объект 🏢 ', callback_data=f'attach_facility {attach_user_id} {city}')],
    ]

    @registration_router.callback_query(F.data.startswith('attach_facility'))
    async def handle_attach_facility_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling attach_facility location button callback from user {callback.message.chat.id}')
        from .facilities import get_choose_facility_inline_keyboard
        data = callback.data.split()
        attach_user_id_, city_ = int(data[1]), data[2]
        user = await db.users.get_by_id(user_id=attach_user_id_)
        await callback.message.delete()
        await callback.message.answer(
            text=strs.facility_choose_available(city=city_, name=user.fullname),
            reply_markup=await get_choose_facility_inline_keyboard(attach_to=attach_user_id_, city=city_)
        )

    return InlineKeyboardMarkup(inline_keyboard=button_list)


# __chat__ !DO NOT DELETE!
@registration_router.message(Command('registration'))
async def handle_registration_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /registration from user {message.chat.id}')
    user = await db.users.get_by_id(user_id=message.chat.id)
    if not user:
        await message.answer(text=strs.registration_started, reply_markup=await get_decline_reply_keyboard())
        await state.set_state(RegistrationStates.get_fullname.state)
    else:
        await message.answer(text=strs.registration_already)


@registration_router.message(RegistrationStates.get_fullname)
async def handle_get_fullname_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states RegistrationStates.get_fullname from user {message.from_user.id}')
    fullname = message.text
    if fullname:
        await state.update_data({'fullname': fullname})
        await message.answer(text=strs.registration_ask_post)
        await state.set_state(RegistrationStates.get_post.state)
    else:
        await message.answer(text=strs.registration_fullname_error)


@registration_router.message(RegistrationStates.get_post)
async def handle_get_post_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states RegistrationStates.get_post from user {message.from_user.id}')
    post = message.text
    if post:
        await state.update_data({'post': post})
        await message.answer(text=strs.registration_ask_city)
        await state.set_state(RegistrationStates.get_city.state)
    else:
        await message.answer(text=strs.registration_post_error)


@registration_router.message(RegistrationStates.get_city)
async def handle_get_city_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states RegistrationStates.get_city from user {message.from_user.id}')
    city = message.text
    if city:
        await state.update_data({'city': city})
        await message.answer(text=strs.registration_ask_age)
        await state.set_state(RegistrationStates.get_age.state)
    else:
        await message.answer(text=strs.registration_city_error)


@registration_router.message(RegistrationStates.get_age)
async def handle_get_age_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states RegistrationStates.get_age from user {message.from_user.id}')
    age = message.text
    if age and age.isdigit():
        age = int(age)

        if age <= 0 or age >= 100:
            await message.answer(text=strs.registration_ask_phone)
            return

        await state.update_data({'age': age})
        await message.answer(text=strs.registration_ask_phone)
        await state.set_state(RegistrationStates.get_phone.state)
    else:
        await message.answer(text=strs.registration_age_error)


@registration_router.message(RegistrationStates.get_phone)
async def handle_get_phone_state(message: Message, state: FSMContext):
    import re
    bot_logger.info(f'Handling states RegistrationStates.get_phone from user {message.from_user.id}')
    phone = message.text
    phone_matcher = re.compile(r'^\+?\d{10,15}$')
    if phone and phone_matcher.match(phone):
        await state.update_data({'phone': phone})
        await message.answer(text=strs.registration_ask_photo)
        await state.set_state(RegistrationStates.get_photo.state)
    else:
        await message.answer(text=strs.registration_phone_error)


@registration_router.message(RegistrationStates.get_photo)
async def handle_get_photo_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states RegistrationStates.get_photo from user {message.from_user.id}')
    from handlers.utils import download_image
    import os
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

        data = await state.get_data()
        user = UserModel()
        user.id = message.chat.id
        user.fullname = data['fullname']
        user.post = data['post']
        user.city = data['city'].lower().capitalize()
        user.age = data['age']
        user.phone = data['phone']
        user.photo = url
        await db.users.insert(user=user)
        await message.answer(text=strs.registration_successfully, reply_markup=ReplyKeyboardRemove())

        admins = await db.users.get_all_admins()
        if admins:
            for admin in admins:
                user_info = strs.registration_new_user(
                    fullname=data['fullname'], post=data['post'], city=data['city'].lower().capitalize(),
                    age=data['age'], phone=data['phone']
                )
                await message.bot.send_photo(
                    chat_id=admin.id,
                    photo=FSInputFile(path=destination),
                    caption=user_info,
                    reply_markup=await get_attach_facility_keyboard(
                        attach_user_id=message.chat.id,
                        city=data['city'].lower().capitalize()
                    )
                )

        await state.clear()
    else:
        await message.answer(text=strs.registration_photo_error)
