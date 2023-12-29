from . import *

# __router__ !DO NOT DELETE!
shift_router = Router()


# __states__ !DO NOT DELETE!
class StartShiftStates(StatesGroup):
    get_geo = State()
    get_photo = State()
    get_name = State()


# __buttons__ !DO NOT DELETE
async def get_decline_reply_keyboard() -> ReplyKeyboardMarkup:
    button_list = [
        [KeyboardButton(text=strs.decline_btn)],
    ]

    return ReplyKeyboardMarkup(keyboard=button_list, resize_keyboard=True, one_time_keyboard=True)


async def get_geo_reply_keyboard() -> ReplyKeyboardMarkup:
    button_list = [
        [KeyboardButton(text='Отправить координаты 🗺️', request_location=True)],
        [KeyboardButton(text=strs.decline_btn)],
    ]

    return ReplyKeyboardMarkup(keyboard=button_list, one_time_keyboard=True, resize_keyboard=True)


# __chat__ !DO NOT DELETE!
@shift_router.message(Private(), Command('start_shift'))
async def handle_start_shift_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /start_shift from user {message.chat.id}')
    user = await db.users.get_by_id(user_id=message.chat.id)
    if user:
        shifts = await db.users.get_all_shifts(user_id=message.chat.id)
        if shifts:
            for shift_ in shifts:
                if shift_.end_time is None:
                    await message.answer(text=strs.shift_already_started)
                    return

        if user.current_facility_id:
            facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)
            if facility:
                await message.answer(text=strs.shift_ask_geo(dist_range=facility.access_get_range), reply_markup=await get_geo_reply_keyboard())
                await state.set_state(StartShiftStates.get_geo.state)
            else:
                await message.answer(text=strs.shift_no_such_facility)
        else:
            await message.answer(text=strs.shift_choose_facility)
    else:
        await message.answer(text=strs.shift_choose_facility)


@shift_router.message(StartShiftStates.get_geo)
async def handle_get_geo_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states StartShiftStates.get_geo from user {message.from_user.id}')
    import re
    import geopy.distance as distance

    location = message.location
    string_geo = message.text
    geo_matcher = re.compile(r'^\d*\.?\d*,? \d*\.?\d*$')
    if location:
        user = await db.users.get_by_id(user_id=message.from_user.id)
        if user:
            facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)
            if facility:
                curr_pos = (location.latitude, location.longitude)
                facility_pos = tuple(el for el in facility.geo.replace(',', '').split())
                dist = distance.geodesic(curr_pos, facility_pos).meters
                bot_logger.info(f'Distance between user {user.fullname} and facility {facility.name} is {dist}')
                if dist <= facility.access_get_range:
                    await state.update_data({
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'distance': dist
                    })
                    await message.answer(text=strs.shift_ask_facility_photo,
                                         reply_markup=await get_decline_reply_keyboard())
                    await state.set_state(StartShiftStates.get_photo.state)
                else:
                    await message.answer(text=strs.shift_too_far(distance=dist))
            else:
                await message.answer(text=strs.shift_no_such_facility)
        else:
            await message.answer(text=strs.no_such_user)
    elif string_geo and geo_matcher.match(string_geo):
        user = await db.users.get_by_id(user_id=message.from_user.id)
        if user:
            facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)
            if facility:
                latitude, longitude = string_geo.replace(',', '').split()
                curr_pos = (latitude, longitude)
                facility_pos = tuple(el for el in facility.geo.replace(',', '').split())
                dist = distance.geodesic(curr_pos, facility_pos).meters
                if dist < 60:
                    await state.update_data({
                        'latitude': latitude,
                        'longitude': longitude,
                        'distance': dist
                    })
                    await message.answer(text=strs.shift_ask_facility_photo,
                                         reply_markup=await get_decline_reply_keyboard())
                    await state.set_state(StartShiftStates.get_photo.state)
                else:
                    await message.answer(text=strs.shift_too_far(distance=dist))
            else:
                await message.answer(text=strs.shift_no_such_facility)
        else:
            await message.answer(text=strs.no_such_user)
    else:
        await message.answer(text=strs.shift_geo_error)


@shift_router.message(StartShiftStates.get_photo)
async def handle_get_photo_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states StartShiftStates.get_photo from user {message.from_user.id}')
    import os
    from uuid import uuid4
    from datetime import datetime, timezone, timedelta
    from handlers.utils import download_image
    photo = message.photo
    if photo:
        file = await message.bot.get_file(file_id=photo[-1].file_id)
        url = f'https://api.telegram.org/file/bot{cf.bot["token"]}/{file.file_path}'

        user = await db.users.get_by_id(user_id=message.from_user.id)
        if user:
            facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)
            if facility:
                folder_path = f'media/{message.from_user.id}/images/facilities'
                if not os.path.exists(cf.BASE + '/' + folder_path):
                    os.makedirs(cf.BASE + '/' + folder_path, exist_ok=True)

                destination = f'{folder_path}/{facility.id}.png'
                is_successfully = await download_image(image_url=url, destination=destination)
                if is_successfully:
                    url = f'http://{cf.panel_server["host"]}:{cf.panel_server["port"]}/get/{destination}'

                    data = await state.get_data()
                    latitude, longitude = data['latitude'], data['longitude']
                    shift_ = ShiftModel()
                    shift_id = str(uuid4())[:10]
                    shift_.id = shift_id
                    shift_.start_time = datetime.now(timezone(timedelta(hours=3))) + timedelta(hours=3)
                    shift_.photo = url
                    shift_.user_id = message.from_user.id
                    shift_.user_geo = f'{latitude} {longitude}'
                    shift_.distance_facility_user = data['distance']
                    shift_.facility_id = facility.id
                    await db.shifts.insert(shift=shift_)
                    await db.users.add_shift(user_id=message.from_user.id, shift_id=shift_id)
                    await message.answer(text=strs.shift_successfully_started, reply_markup=ReplyKeyboardRemove())
                    await state.clear()
                    await state.clear()
            else:
                await message.answer(text=strs.shift_no_such_facility)
        else:
            await message.answer(text=strs.no_such_user)
    else:
        await message.answer(text=strs.shift_facility_photo_error)


@shift_router.message(Private(), Command('end_shift'))
async def handle_end_shift_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /end_shift from user {message.from_user.id}')
    user = await db.users.get_by_id(user_id=message.chat.id)
    if user:
        shifts = await db.users.get_all_shifts(user_id=message.chat.id)
        if shifts:
            for shift_ in shifts:
                if shift_.end_time is None:
                    from datetime import datetime, timedelta, timezone
                    from handlers.utils import format_timedelta_to_hours_minutes, convert_time_to_float
                    shift_.end_time = datetime.now(timezone(timedelta(hours=3)))
                    time_difference = shift_.end_time - (shift_.start_time.replace(tzinfo=timezone(timedelta(hours=3))))
                    total_time = await format_timedelta_to_hours_minutes(timedelta_obj=time_difference)
                    shift_.total_time = total_time
                    user.hours = round(user.hours + await convert_time_to_float(time_str=total_time), 2)
                    user.income = round(user.hours * user.rate_an_hour, 2)
                    await db.users.update(user=user)
                    await db.shifts.update(shift=shift_)
                    await message.answer(text=strs.shift_successfully_ended(
                        start_time=str(shift_.start_time).split('.')[0], end_time=str(shift_.end_time).split('.')[0],
                        total=shift_.total_time, income=round(await convert_time_to_float(time_str=total_time))
                    ))
                    return
            await message.answer(text=strs.shift_no_opened_shifts)
        else:
            await message.answer(text=strs.shift_no_opened_shifts)
