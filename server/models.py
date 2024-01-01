# Third-party
from sqladmin import ModelView
from starlette.responses import HTMLResponse

# Project
from database import UserModel, ShiftModel, FacilityModel, QuestionModel, ReportModel, LogModel


class UserView(ModelView, model=UserModel):
    name = 'Пользователь'
    name_plural = 'Пользователи'
    column_labels = {
        UserModel.id: 'ID телеграм',
        UserModel.fullname: 'Имя',
        UserModel.is_admin: 'Администратор?',
        UserModel.post: 'Должность',
        UserModel.city: 'Город',
        UserModel.age: 'Возраст',
        UserModel.phone: 'Телефон',
        UserModel.photo: 'Фото',
        UserModel.current_facility_id: 'ID текущего объекта',
        UserModel.income: 'Доход',
        UserModel.hours: 'Часы',
        UserModel.last_month_income: 'Доход за прошлый месяц',
        UserModel.last_month_hours: 'Отработанные час за прошлый месяц',
        UserModel.rate_an_hour: 'Ставка за час',
        UserModel.complain: 'Замечание',
    }
    column_details_exclude_list = [
        UserModel.shifts,
    ]
    column_list = [
        UserModel.id,
        UserModel.fullname,
        UserModel.is_admin,
        UserModel.post,
        UserModel.city,
        UserModel.age,
        UserModel.phone,
        UserModel.photo,
        UserModel.current_facility_id,
        UserModel.income,
        UserModel.hours,
        UserModel.last_month_income,
        UserModel.last_month_hours,
        UserModel.rate_an_hour,
        UserModel.complain
    ]
    column_sortable_list = column_list
    column_searchable_list = [
        UserModel.fullname,
        UserModel.city,
        UserModel.post,
        UserModel.phone,
        UserModel.id
    ]


class ShiftView(ModelView, model=ShiftModel):
    name = 'Смена'
    name_plural = 'Смены'
    column_labels = {
        ShiftModel.id: 'ID',
        ShiftModel.start_time: 'Начало смены по МСК',
        ShiftModel.end_time: 'Конец смены по МСК',
        ShiftModel.total_time: 'Общее время (ч:мин)',
        ShiftModel.photo: 'Фото',
        ShiftModel.user_id: 'ID пользователя',
        ShiftModel.user_geo: 'Геопозиция пользователя',
        ShiftModel.distance_facility_user: 'Расстояние до объекта',
        ShiftModel.facility_id: 'ID объекта',
    }
    column_details_exclude_list = [
        ShiftModel.user
    ]
    column_list = [
        ShiftModel.id,
        ShiftModel.start_time,
        ShiftModel.end_time,
        ShiftModel.total_time,
        ShiftModel.photo,
        ShiftModel.user_id,
        ShiftModel.user_geo,
        ShiftModel.distance_facility_user,
        ShiftModel.facility_id,
    ]
    column_sortable_list = column_list
    column_searchable_list = [ShiftModel.id, ShiftModel.user_id, ShiftModel.facility_id]


class FacilityView(ModelView, model=FacilityModel):
    name = 'Объект'
    name_plural = 'Объекты'
    column_labels = {
        FacilityModel.id: 'ID',
        FacilityModel.name: 'Название',
        FacilityModel.geo: 'Геопозиция',
        FacilityModel.city: 'Город',
        FacilityModel.access_get_range: 'Допустимый радиус удаления (метры)',
        FacilityModel.work_start_time: 'Начало работы по МСК',
        FacilityModel.work_end_time: 'Конец работы по МСК',
    }
    column_list = [
        FacilityModel.id,
        FacilityModel.name,
        FacilityModel.geo,
        FacilityModel.city,
        FacilityModel.access_get_range,
        FacilityModel.work_start_time,
        FacilityModel.work_end_time,
    ]
    column_sortable_list = column_list
    column_searchable_list = [FacilityModel.id, FacilityModel.name, FacilityModel.city, FacilityModel.access_get_range]


class QuestionView(ModelView, model=QuestionModel):
    name = 'Вопрос'
    name_plural = 'Вопросы'
    column_labels = {
        QuestionModel.id: 'ID',
        QuestionModel.user_name: 'Кто задал вопрос?',
        QuestionModel.from_user_id: 'ID пользователя',
        QuestionModel.is_closed: 'Ответили ли?',
        QuestionModel.date: 'Время появления по МСК',
        QuestionModel.close_date: 'Время закрытия по МСК',
        QuestionModel.content: 'Вопрос',
        QuestionModel.tg_info: 'Содержимое (ТГ)',
    }
    column_list = [
        QuestionModel.id,
        QuestionModel.user_name,
        QuestionModel.from_user_id,
        QuestionModel.is_closed,
        QuestionModel.date,
        QuestionModel.close_date,
        QuestionModel.content,
    ]
    column_sortable_list = column_list
    column_searchable_list = [QuestionModel.id, QuestionModel.user_name, QuestionModel.date, QuestionModel.close_date, QuestionModel.from_user_id]


class ReportView(ModelView, model=ReportModel):
    name = 'Отчет'
    name_plural = 'Отчеты'
    column_labels = {
        ReportModel.id: 'ID',
        ReportModel.is_monthly: 'Ежемесячный?',
        ReportModel.user_id: 'ID пользователя',
        ReportModel.user_name: 'Имя пользователя',
        ReportModel.date_range: 'Диапазон дат',
        ReportModel.file: 'Файл',
    }
    column_list = [
        ReportModel.id,
        ReportModel.is_monthly,
        ReportModel.user_id,
        ReportModel.user_name,
        ReportModel.date_range,
        ReportModel.file,
    ]
    column_sortable_list = column_list
    column_searchable_list = [ReportModel.id, ReportModel.user_id, ReportModel.user_name]


class LogView(ModelView, model=LogModel):
    name = 'Лог'  # Display name for single entry
    name_plural = 'Логи'  # Display name for multiple entries
    column_labels = {
        LogModel.id: 'ID',
        LogModel.file: 'Файл',
    }
    column_list = [
        LogModel.id,
        LogModel.file,
    ]
    column_sortable_list = column_list  # Indicate which columns can be sorted
    column_searchable_list = [LogModel.file]  # Indicate which columns can be searchedф
