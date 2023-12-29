from . import *


# Enum for different types of database connections
class Type(Enum):
    POSTGRESQL = f'postgresql+psycopg2://{cf.database["user"]}:{cf.database["password"]}@{cf.database["host"]}:{cf.database["port"]}'


class Database:
    # Private method to connect to the database
    def __connect_to_database(self, type_: Type):
        while True:
            self.logger.warning('Connecting to database...')
            try:
                # Creating a database engine
                self.engine = create_engine(type_.value)
                self.session_maker = sessionmaker(bind=self.engine)
                # Creating tables defined in 'base' metadata
                base.metadata.create_all(self.engine)

                # __connect_inner_classes__ !DO NOT DELETE!

                self.logs = self.Log(session_maker=self.session_maker)
                self.users = self.User(session_maker=self.session_maker)
                self.shifts = self.Shift(session_maker=self.session_maker)
                self.facilities = self.Facility(session_maker=self.session_maker)
                self.questions = self.Question(session_maker=self.session_maker)
                self.reports = self.Report(session_maker=self.session_maker)

                self.logger.info('Connected to database')
                break
            except sqlalchemy.exc.OperationalError:
                # Handling database connection errors
                self.logger.error('Database error:\n' + traceback.format_exc())
                sleep(5.0)

    # Constructor to initialize the Database class
    def __init__(self, type_: Type):
        self.logger = database_logger
        self.__connect_to_database(type_=type_)

    # __inner_classes__ !DO NOT DELETE!
    class Log:
        def __init__(self, session_maker):
            self.session_maker = session_maker

        async def insert(self, log: LogModel):
            with self.session_maker() as session:
                session.add(log)
                session.commit()
                database_logger.info(f'LogModel is created!')
                session.close()

        async def get_all(self) -> list[LogModel] | None:
            with self.session_maker() as session:
                data = session.query(LogModel).all()
                if data:
                    database_logger.info('Fetched all LogModels')
                    return data
                else:
                    database_logger.info('No LogModels in a database')
                    return None

        async def get_by_id(self, log_id: str) -> LogModel | None:
            with self.session_maker() as session:
                data = session.query(LogModel).filter_by(id=id).first()
                if data:
                    database_logger.info(f'LogModel {id} is retrieved from database')
                    session.close()
                    return data
                else:
                    database_logger.info(f'LogModel {id} is not in database')
                    session.close()
                    return None

        async def delete(self, log: LogModel):
            with self.session_maker() as session:
                session.query(LogModel).filter_by(id=log.id).delete()
                database_logger.warning(f'LogModel {log.id} is deleted!')
                session.commit()
                session.close()

        async def update(self, log: LogModel):
            with self.session_maker() as session:
                session.query(LogModel).filter_by(id=log.id).update({
                    'file': log.file,
                })
                database_logger.warning(f'LogModel {log.id} is updated!')
                session.commit()
                session.close()

    class Report:
        def __init__(self, session_maker):
            self.session_maker = session_maker

        async def insert(self, report: ReportModel):
            with self.session_maker() as session:
                session.add(report)
                session.commit()
                database_logger.info(f'ReportModel is created!')
                session.close()

        async def get_all(self) -> list[ReportModel] | None:
            with self.session_maker() as session:
                data = session.query(ReportModel).all()
                if data:
                    database_logger.info('Fetched all ReportModels')
                    return data
                else:
                    database_logger.info('No ReportModels in a database')
                    return None

        async def get_by_id(self, report_id: str) -> ReportModel | None:
            with self.session_maker() as session:
                data = session.query(ReportModel).filter_by(id=report_id).first()
                if data:
                    database_logger.info(f'ReportModel {report_id} is retrieved from database')
                    session.close()
                    return data
                else:
                    database_logger.info(f'ReportModel {report_id} is not in database')
                    session.close()
                    return None

        async def delete(self, report: ReportModel):
            with self.session_maker() as session:
                session.query(ReportModel).filter_by(id=report.id).delete()
                database_logger.warning(f'ReportModel {report.id} is deleted!')
                session.commit()
                session.close()

        async def update(self, report: ReportModel):
            with self.session_maker() as session:
                session.query(ReportModel).filter_by(id=report.id).update({
                    'is_monthly': report.is_monthly,
                    'user_id': report.user_id,
                    'user_name': report.user_name,
                    'file': report.file,
                    'date_range': report.date_range
                })
                database_logger.warning(f'ReportModel {report.id} is updated!')
                session.commit()
                session.close()

    class Question:
        def __init__(self, session_maker):
            self.session_maker = session_maker

        async def insert(self, question: QuestionModel):
            with self.session_maker() as session:
                session.add(question)
                session.commit()
                database_logger.info(f'QuestionModel is created!')
                session.close()

        async def get_all(self) -> list[QuestionModel] | None:
            with self.session_maker() as session:
                data = session.query(QuestionModel).all()
                if data:
                    database_logger.info('Fetched all QuestionModels')
                    return data
                else:
                    database_logger.info('No QuestionModels in a database')
                    return None

        async def get_last_user_question(self, user_id: int) -> QuestionModel | None:
            with self.session_maker() as session:
                data = session.query(QuestionModel).filter_by(from_user_id=user_id).all()
                if data:
                    database_logger.info(f'Fetched all QuestionModels of user {user_id}')
                    return sorted(data, key=lambda question: question.date)[-1]
                else:
                    database_logger.info('No QuestionModels in a database')
                    return None

        async def get_by_id(self, question_id: str) -> QuestionModel | None:
            with self.session_maker() as session:
                data = session.query(QuestionModel).filter_by(id=question_id).first()
                if data:
                    database_logger.info(f'QuestionModel {question_id} is retrieved from database')
                    session.close()
                    return data
                else:
                    database_logger.info(f'QuestionModel {question_id} is not in database')
                    session.close()
                    return None

        async def delete(self, question: QuestionModel):
            with self.session_maker() as session:
                session.query(QuestionModel).filter_by(id=question.id).delete()
                database_logger.warning(f'QuestionModel {question.id} is deleted!')
                session.commit()
                session.close()

        async def update(self, question: QuestionModel):
            with self.session_maker() as session:
                session.query(QuestionModel).filter_by(id=question.id).update({
                    'from_user_id': question.from_user_id,
                    'date': question.date,
                    'content': question.content,
                    'tg_info': question.tg_info
                })
                database_logger.warning(f'QuestionModel {question.id} is updated!')
                session.commit()
                session.close()

    class User:
        def __init__(self, session_maker):
            self.session_maker = session_maker

        async def insert(self, user: UserModel):
            with self.session_maker() as session:
                session.add(user)
                session.commit()
                database_logger.info(f'UserModel is created!')
                session.close()

        async def get_all(self) -> list[UserModel] | None:
            with self.session_maker() as session:
                data = session.query(UserModel).all()
                if data:
                    database_logger.info('Fetched all UserModels')
                    return data
                else:
                    database_logger.info('No UserModels in a database')
                    return None

        async def get_all_unemployed(self) -> list[UserModel] | None:
            with self.session_maker() as session:
                data = session.query(UserModel).filter_by(current_facility_id=None).all()
                if data:
                    database_logger.info('Fetched all unemployed users')
                    return data
                else:
                    database_logger.info('No unemployed users in a database')
                    return None

        async def get_all_admins(self) -> list[UserModel] | None:
            with self.session_maker() as session:
                data = session.query(UserModel).filter_by(is_admin=True).all()
                if data:
                    database_logger.info('Fetched all admins')
                    return data
                else:
                    database_logger.info('No admins in database')
                    return None

        async def get_by_id(self, user_id: int) -> UserModel | None:
            with self.session_maker() as session:
                data = session.query(UserModel).filter_by(id=user_id).first()
                if data:
                    database_logger.info(f'UserModel {user_id} is retrieved from database')
                    session.close()
                    return data
                else:
                    database_logger.info(f'UserModel {user_id} is not in database')
                    session.close()
                    return None

        async def delete(self, user: UserModel):
            with self.session_maker() as session:
                session.query(UserModel).filter_by(id=user.id).delete()
                database_logger.warning(f'UserModel {user.id} is deleted!')
                session.commit()
                session.close()

        async def update(self, user: UserModel):
            with self.session_maker() as session:
                session.query(UserModel).filter_by(id=user.id).update({
                    'fullname': user.fullname,
                    'post': user.post,
                    'city': user.city,
                    'age': user.age,
                    'phone': user.phone,
                    'photo': user.photo,
                    'income': user.income,
                    'hours': user.hours,
                    'last_month_income': user.last_month_income,
                    'last_month_hours': user.last_month_hours,
                    'current_facility_id': user.current_facility_id,
                    'rate_an_hour': user.rate_an_hour,
                    'is_start_shift_notified': user.is_start_shift_notified,
                    'is_end_shift_notified': user.is_end_shift_notified
                })
                database_logger.warning(f'UserModel {user.id} is updated!')
                session.commit()
                session.close()

        async def add_shift(self, user_id: int, shift_id: str):
            with self.session_maker() as session:
                user = session.query(UserModel).get(user_id)
                shift = session.query(ShiftModel).get(shift_id)
                if user and shift:
                    user.shifts.append(shift)
                    session.commit()
                    database_logger.info(f'Shift {shift_id} associated with User {user_id}')
                    session.close()
                else:
                    database_logger.warning('User or Shift not found')

        async def get_all_shifts(self, user_id: int) -> list[ShiftModel] | None:
            with self.session_maker() as session:
                user = session.query(UserModel).get(user_id)
                if user:
                    shifts = user.shifts
                    closed_shifts = []
                    started_shifts = []
                    if shifts:
                        for shift in shifts:
                            if shift.end_time is None:
                                started_shifts.append(shift)
                            else:
                                closed_shifts.append(shift)
                    closed_shifts = sorted(closed_shifts, key=lambda shift_: shift_.end_time)
                    database_logger.info(f'Fetched all shifts for UserModel {user_id}')
                    session.close()
                    return started_shifts + closed_shifts
                else:
                    database_logger.info(f'UserModel {user_id} not found')
                    session.close()
                    return None

    class Shift:
        def __init__(self, session_maker):
            self.session_maker = session_maker

        async def insert(self, shift: ShiftModel):
            with self.session_maker() as session:
                session.add(shift)
                session.commit()
                database_logger.info(f'ShiftModel is created!')
                session.close()

        async def get_all(self) -> list[ShiftModel] | None:
            with self.session_maker() as session:
                data = session.query(ShiftModel).all()
                if data:
                    database_logger.info('Fetched all ShiftModels')
                    return data
                else:
                    database_logger.info('No ShiftModels in a database')
                    return None

        async def get_by_id(self, shift_id: str) -> ShiftModel | None:
            with self.session_maker() as session:
                data = session.query(ShiftModel).filter_by(id=shift_id).first()
                if data:
                    database_logger.info(f'ShiftModel {shift_id} is retrieved from database')
                    session.close()
                    return data
                else:
                    database_logger.info(f'ShiftModel {shift_id} is not in database')
                    session.close()
                    return None

        async def delete(self, shift: ShiftModel):
            with self.session_maker() as session:
                session.query(ShiftModel).filter_by(id=shift.id).delete()
                database_logger.warning(f'ShiftModel {shift.id} is deleted!')
                session.commit()
                session.close()

        async def update(self, shift: ShiftModel):
            with self.session_maker() as session:
                session.query(ShiftModel).filter_by(id=shift.id).update({
                    'start_time': shift.start_time,
                    'end_time': shift.end_time,
                    'total_time': shift.total_time,
                    'user_id': shift.user_id,
                    'user_geo': shift.user_geo,
                    'distance_facility_user': shift.distance_facility_user,
                    'facility_id': shift.facility_id
                })
                database_logger.warning(f'ShiftModel {shift.id} is updated!')
                session.commit()
                session.close()

    class Facility:
        def __init__(self, session_maker):
            self.session_maker = session_maker

        async def insert(self, facility: FacilityModel):
            with self.session_maker() as session:
                session.add(facility)
                session.commit()
                database_logger.info(f'FacilityModel is created!')
                session.close()

        async def get_all(self) -> list[FacilityModel] | None:
            with self.session_maker() as session:
                data = session.query(FacilityModel).all()
                if data:
                    database_logger.info('Fetched all FacilityModels')
                    return data
                else:
                    database_logger.info('No FacilityModels in a database')
                    return None

        async def get_all_by_city(self, city: str) -> list[FacilityModel] | None:
            with self.session_maker() as session:
                data = session.query(FacilityModel).filter_by(city=city.lower().capitalize()).all()
                if data:
                    database_logger.info(f'Fetched all FacilityModels of {city}')
                    return data
                else:
                    database_logger.info(f'No FacilityModels of {city} in a database')
                    return None

        async def get_by_id(self, facility_id: str) -> FacilityModel | None:
            with self.session_maker() as session:
                data = session.query(FacilityModel).filter_by(id=facility_id).first()
                if data:
                    database_logger.info(f'FacilityModel {facility_id} is retrieved from database')
                    session.close()
                    return data
                else:
                    database_logger.info(f'FacilityModel {facility_id} is not in database')
                    session.close()
                    return None

        async def delete(self, facility: FacilityModel):
            with self.session_maker() as session:
                session.query(FacilityModel).filter_by(id=facility.id).delete()
                database_logger.warning(f'FacilityModel {facility.id} is deleted!')
                session.commit()
                session.close()

        async def update(self, facility: FacilityModel):
            with self.session_maker() as session:
                session.query(FacilityModel).filter_by(id=facility.id).update({
                    'name': facility.name,
                    'geo': facility.geo,
                    'city': facility.city,
                    'access_get_range': facility.distance_facility_user,
                    'work_start_time': facility.work_start_time,
                    'work_end_time': facility.work_end_time
                })
                database_logger.warning(f'FacilityModel {facility.id} is updated!')
                session.commit()
                session.close()


db = Database(type_=Type.POSTGRESQL)
