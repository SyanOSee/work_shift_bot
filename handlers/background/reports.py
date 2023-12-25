# Project
from database import db, UserModel, ReportModel
import config as cf
import pandas as pd
from handlers.utils import convert_time_to_float

# Standard
from datetime import datetime, timezone, timedelta
import os


async def get_report(user: UserModel, start_time: datetime, end_time: datetime) -> pd.DataFrame:
    shifts = await db.users.get_all_shifts(user_id=user.id)
    shifts_count = 0
    hours = 0
    if shifts:
        for shift in shifts:
            if shift.end_time:
                time_boundaries = start_time <= shift.end_time.replace(tzinfo=timezone(timedelta(hours=3))) <= end_time
                if shift.end_time and time_boundaries:
                    shifts_count += 1
                    hours += await convert_time_to_float(time_str=shift.total_time)

    report_data = {
        'Сотрудник': user.fullname,
        'Количество смен': shifts_count,
        'Количество часов': hours,
        'Ставка в час, руб': user.rate_an_hour,
        'Итоговая сумма, руб': hours * user.rate_an_hour
    }
    return pd.DataFrame([report_data])


async def generate_report(is_weekly: bool):
    reports_list = []

    current_time = datetime.now(timezone(timedelta(hours=3)))
    if is_weekly:
        days_to_monday = current_time.weekday()
        start_date = current_time - timedelta(days=days_to_monday)
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = start_date + timedelta(days=6)
        end_date = end_date.replace(hour=0, minute=0, second=0)
    else:
        first_day_of_current_month = current_time.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        start_date = last_day_of_previous_month.replace(day=25)
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = current_time.replace(day=25)
        end_date = end_date.replace(hour=0, minute=0, second=0)

    users = await db.users.get_all()
    reports_list.append(
        pd.DataFrame([{
            'Отчет по заработной плате': f'{start_date.strftime("%Y-%m-%d")} - {end_date.strftime("%Y-%m-%d")}'
        }])
    )
    if users:
        for user in users:
            report_df = await get_report(user=user, start_time=start_date, end_time=end_date)
            reports_list.append(report_df)

            final_report_df = pd.concat(reports_list, ignore_index=True)
            folder_name = 'weekly' if is_weekly else 'monthly'
            file_name = f'{folder_name}_report_{start_date.strftime("%Y-%m-%d")}_to_{end_date.strftime("%Y-%m-%d")}.xlsx'
            folder_path = cf.BASE + f'/media/reports/{folder_name}'

            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)

            csv_file_path = os.path.join(folder_path, file_name)
            final_report_df.to_excel(csv_file_path, index=False, header=True)

            report = ReportModel()
            url = f'http://{cf.media_server["host"]}:{cf.media_server["port"]}/get/{csv_file_path}'
            report.file = url
            report.date_range = f'{start_date.strftime("%Y-%m-%d")} - {end_date.strftime("%Y-%m-%d")}'
            await db.reports.insert(report=report)
            if not is_weekly:
                user.last_month_income = user.income
                user.last_month_hours = user.hours
                user.income = 0
                user.hours = 0
                await db.users.update(user=user)
