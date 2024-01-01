# Project
from database import db, UserModel, ReportModel
import config as cf
from logger import background_logger
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

    facility = None
    if user.current_facility_id:
        facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)

    report_data = {
        'Сотрудник': user.fullname,
        'Telegram ID': user.id,
        'Должность': user.post,
        'Количество смен': len(shifts) if shifts else 0,
        'Фотография': user.photo,
        'Объект': facility.name if facility else 'Отсутствует',
        'Открытие': facility.work_start_time if facility else '-',
        'Закрытие': facility.work_end_time if facility else '-',
        'Количество часов за месяц': user.hours,
        'Ставка в час, руб': user.rate_an_hour,
        'Итоговая сумма за месяц, руб': user.income,
        'Количество часов за прошлый месяц': user.last_month_hours,
        'Итоговая сумма за прошлый месяц': user.last_month_income,
        'Номер для связи': user.phone,
        'Замечание': user.complain
    }
    return pd.DataFrame([report_data])


async def generate_week_report():
    reports_list = []

    current_time = datetime.now(timezone(timedelta(hours=3)))
    days_to_monday = current_time.weekday()
    start_date = current_time - timedelta(days=days_to_monday)
    start_date = start_date.replace(hour=0, minute=0, second=0)
    end_date = start_date + timedelta(days=6)
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
            folder_name = 'weekly'
            file_name = f'{folder_name}_report_{start_date.strftime("%Y-%m-%d")}_to_{end_date.strftime("%Y-%m-%d")}.xlsx'
            folder_path = cf.BASE + f'/media/reports/{folder_name}'

            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)

            csv_file_path = os.path.join(folder_path, file_name)
            final_report_df.to_excel(csv_file_path, index=False, header=True)

            report = ReportModel()
            url = f'http://{cf.panel_server["host"]}:{cf.panel_server["port"]}/get/{csv_file_path}'
            report.file = url
            report.date_range = f'{start_date.strftime("%Y-%m-%d")} - {end_date.strftime("%Y-%m-%d")}'
            await db.reports.insert(report=report)


async def generate_month_report():
    reports_list = []

    current_time = datetime.now(timezone(timedelta(hours=3)))
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
            folder_name = 'monthly'
            file_name = f'{folder_name}_report_{start_date.strftime("%Y-%m-%d")}_to_{end_date.strftime("%Y-%m-%d")}.xlsx'
            folder_path = cf.BASE + f'/media/reports/{folder_name}'

            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)

            csv_file_path = os.path.join(folder_path, file_name)
            final_report_df.to_excel(csv_file_path, index=False, header=True)

            report = ReportModel()
            url = f'http://{cf.panel_server["host"]}:{cf.panel_server["port"]}/get/{csv_file_path}'
            report.file = url
            report.date_range = f'{start_date.strftime("%Y-%m-%d")} - {end_date.strftime("%Y-%m-%d")}'
            await db.reports.insert(report=report)
            user.last_month_income = user.income
            user.last_month_hours = user.hours
            user.income = 0
            user.hours = 0
            await db.users.update(user=user)


async def generate_facility_users_report(facility_id):
    background_logger.info(f'Starting to generate report for facility with id {facility_id}')
    facility = await db.facilities.get_by_id(facility_id=facility_id)
    if facility:
        path = cf.BASE + f'/media/reports/facilities/{facility.id}'
        if not os.path.exists(path):
            os.makedirs(path)
        report_data = []
        facility_users = await db.users.get_all_with_facility_id(facility_id=facility.id)
        if facility_users:
            for user in facility_users:
                shifts = await db.users.get_all_shifts(user_id=user.id)
                user_report = {
                    'Сотрудник': user.fullname,
                    'Telegram ID': user.id,
                    'Должность': user.post,
                    'Количество смен': len(shifts) if shifts else 0,
                    'Фотография': user.photo,
                    'Объект': facility.name if facility else 'Отсутствует',
                    'Открытие': facility.work_start_time if facility else '-',
                    'Закрытие': facility.work_end_time if facility else '-',
                    'Количество часов за месяц': user.hours,
                    'Ставка в час, руб': user.rate_an_hour,
                    'Итоговая сумма за месяц, руб': user.income,
                    'Количество часов за прошлый месяц': user.last_month_hours,
                    'Итоговая сумма за прошлый месяц': user.last_month_income,
                    'Номер для связи': user.phone,
                    'Замечание': user.complain
                }
                report_data.append(user_report)

        path = cf.BASE + f'{path}/users_report.xlsx'
        report_df = pd.DataFrame(report_data)
        report_df.to_excel(path, index=False, header=True)
        background_logger.info('All users report is created!')


async def generate_users_report():
    background_logger.info('Starting to generate all users report')
    users = await db.users.get_all()  # Replace this with your actual DB call
    if users:
        report_data = []
        for user in users:
            shifts = await db.users.get_all_shifts(user_id=user.id)
            facility = await db.facilities.get_by_id(facility_id=user.current_facility_id)
            user_report = {
                'Сотрудник': user.fullname,
                'Telegram ID': user.id,
                'Должность': user.post,
                'Количество смен': len(shifts) if shifts else 0,
                'Фотография': user.photo,
                'Объект': facility.name if facility else 'Отсутствует',
                'Открытие': facility.work_start_time if facility else '-',
                'Закрытие': facility.work_end_time if facility else '-',
                'Количество часов за месяц': user.hours,
                'Ставка в час, руб': user.rate_an_hour,
                'Итоговая сумма за месяц, руб': user.income,
                'Количество часов за прошлый месяц': user.last_month_hours,
                'Итоговая сумма за прошлый месяц': user.last_month_income,
                'Номер для связи': user.phone,
                'Замечание': user.complain
            }
            report_data.append(user_report)

        path = cf.BASE + f'/media/reports/users_report.xlsx'
        report_df = pd.DataFrame(report_data)
        report_df.to_excel(path, index=False, header=True)
        background_logger.info('All users report is created!')
