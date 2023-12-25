from . import *

# __router__ !DO NOT DELETE!
questions_router = Router()


# __states__ !DO NOT DELETE!
class QuestionStates(StatesGroup):
    get_question = State()


class ReplyStates(StatesGroup):
    get_reply = State()


# __buttons__ !DO NOT DELETE!
async def get_reply_answer_inline_keyboard(question_id: str) -> InlineKeyboardMarkup:
    button_list = [
        [InlineKeyboardButton(text='Ответить 💬', callback_data=f'reply_btn {question_id}'),
         InlineKeyboardButton(text='Отклонить 🚫', callback_data=f'decline_btn {question_id}')],
    ]

    @questions_router.callback_query(F.data.startswith('reply_btn'))
    async def handle_reply_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling reply_answer reply button callback from user {callback.message.chat.id}')
        del_msg_id = callback.message.message_id
        data = callback.data.split()
        question_id = data[1]
        await state.update_data({'question_id': question_id})
        await callback.message.answer(text=strs.question_ask_reply, reply_markup=await get_decline_reply_keyboard())
        await state.set_state(ReplyStates.get_reply.state)

        @questions_router.message(ReplyStates.get_reply)
        async def handle_get_reply_state(message: Message, state: FSMContext):
            bot_logger.info(f'Handling ReplyStates get_reply state from user {message.chat.id}')
            question_id_ = (await state.get_data())['question_id']
            reply_info = message.model_dump()
            if reply_info['text']:
                reply_info['text'] = '<b>Администратор ответил на Ваш вопрос!</b>\n\n' + reply_info['text']
            elif reply_info['caption']:
                reply_info['caption'] = '<b>Администратор ответил на Ваш вопрос!</b>\n\n' + reply_info['caption']
            question = await db.questions.get_by_id(question_id=question_id_)
            if question:
                new_msg = Message(**reply_info)
                await new_msg.send_copy(
                    chat_id=question.from_user_id,
                ).as_(message.bot)
                await db.questions.delete(question=question)
                await message.answer(text=strs.question_successfully_replied, reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer(text=strs.question_another_admin_replied, reply_markup=ReplyKeyboardRemove())
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=del_msg_id)
            except Exception as e:
                bot_logger.error(e)
                bot_logger.warning('Message already deleted!')
            await state.clear()

        await callback.answer()

    @questions_router.callback_query(F.data.startswith('decline_btn'))
    async def handle_decline_button_callback(callback: CallbackQuery, state: FSMContext):
        bot_logger.info(f'Handling reply_answer decline button callback from user {callback.message.chat.id}')
        data = callback.data.split()
        question_id_ = data[1]
        question = await db.questions.get_by_id(question_id=question_id_)
        if question:
            await db.questions.delete(question=question)
            await callback.bot.send_message(chat_id=question.from_user_id, text=strs.question_declined)
            await callback.message.answer(text=strs.question_successfully_declined)
        else:
            await callback.message.answer(text=strs.question_another_admin_declined)
        await callback.message.delete()
        await callback.answer()

    return InlineKeyboardMarkup(inline_keyboard=button_list)


async def get_decline_reply_keyboard() -> ReplyKeyboardMarkup:
    button_list = [
        [KeyboardButton(text=strs.decline_btn)],
    ]

    return ReplyKeyboardMarkup(keyboard=button_list, resize_keyboard=True, one_time_keyboard=True)


# __chat__ !DO NOT DELETE!
@questions_router.message(Private(), Command('question'))
async def handle_question_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /question from user {message.chat.id}')
    from datetime import datetime, timedelta, timezone
    last_question = await db.questions.get_last_user_question(user_id=message.chat.id)
    if last_question:
        current_time = datetime.now(timezone(timedelta(hours=3)))
        last_question_time = last_question.date.replace(tzinfo=timezone(timedelta(hours=3)))
        if current_time < last_question_time + timedelta(minutes=5):
            await message.answer(text=strs.question_too_frequent)
            return
    await message.answer(text=strs.question_example, reply_markup=await get_decline_reply_keyboard())
    await state.set_state(QuestionStates.get_question.state)


@questions_router.message(QuestionStates.get_question)
async def handle_get_question_state(message: Message, state: FSMContext):
    bot_logger.info(f'Handling states QuestionStates.get_question from user {message.chat.id}')
    from uuid import uuid4
    from datetime import datetime, timezone, timedelta

    question_msg_info = message.model_dump()
    current_user = await db.users.get_by_id(user_id=message.chat.id)
    if current_user:
        from_user_question = f'Вопрос задал {current_user.fullname}'
        if question_msg_info['text']:
            question_msg_info['text'] = from_user_question + '\n\n' + question_msg_info['text']
        elif question_msg_info['caption']:
            question_msg_info['caption'] = from_user_question + '\n\n' + question_msg_info['caption']
        question = QuestionModel()
        question_id = str(uuid4())[:10]
        question.id = question_id
        question.date = datetime.now(timezone(timedelta(hours=3))) + timedelta(hours=3)
        question.from_user_id = current_user.id
        question.content = question_msg_info
        await db.questions.insert(question=question)

        users = await db.users.get_all()
        is_send = False
        if users:
            for user in users:
                if user.is_admin:
                    new_message = Message(**question_msg_info)
                    await new_message.send_copy(
                        chat_id=user.id,
                        reply_markup=await get_reply_answer_inline_keyboard(question_id=question_id)
                    ).as_(message.bot)
                    is_send = True
        if not is_send:
            await message.answer(text=strs.question_not_send_but_saved, reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer(text=strs.question_successfully_send, reply_markup=ReplyKeyboardRemove())

    await state.clear()


@questions_router.message(Admin(), Private(), Command('show_questions'))
async def handle_show_questions_command(message: Message, state: FSMContext):
    bot_logger.info(f'Handling command /show_questions from user {message.chat.id}')
    questions_ = await db.questions.get_all()
    if questions_:
        for question in questions_:
            question_msg = Message(**question.content)
            await question_msg.send_copy(
                chat_id=message.chat.id,
                reply_markup=await get_reply_answer_inline_keyboard(question_id=question.id)
            ).as_(message.bot)
    else:
        await message.answer(text=strs.question_no_questions)
