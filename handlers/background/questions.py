# Project
from database import db, QuestionModel

# Standard
from datetime import datetime, timezone, timedelta


async def clear_questions():
    questions = await db.questions.get_all_closed()
    if questions:
        for question in questions:
            close_date = question.close_date.replace(tzinfo=timezone(timedelta(hours=3)))
            current_date = datetime.now(timezone(timedelta(hours=3)))
            if current_date >= close_date + timedelta(days=30):
                await db.questions.delete(question=question)
