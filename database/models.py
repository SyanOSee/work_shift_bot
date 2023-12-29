from . import *

# Standard
from uuid import uuid4
from datetime import datetime, timezone, timedelta

# Creating a base class for declarative models
base = declarative_base()


def get_uuid() -> str:
    return str(uuid4())[:10]


class UserModel(base):
    __tablename__ = 'Users'
    id = Column(BigInteger, primary_key=True)
    fullname = Column(String)
    is_admin = Column(Boolean, default=False)
    post = Column(String)
    city = Column(String)
    age = Column(Integer)
    phone = Column(String)
    photo = Column(String)
    current_facility_id = Column(String, default=None)
    shifts = relationship('ShiftModel', back_populates='user')
    questions = relationship('QuestionModel', back_populates='users')
    reports = relationship('ReportModel', back_populates='users')
    income = Column(Float, default=0)
    hours = Column(Float, default=0)
    last_month_income = Column(Float, default=0)
    last_month_hours = Column(Float, default=0)
    rate_an_hour = Column(Float, default=0)
    is_start_shift_notified = Column(Boolean, default=False)
    is_end_shift_notified = Column(Boolean, default=False)


class ShiftModel(base):
    __tablename__ = 'Shifts'
    id = Column(String, primary_key=True, default=get_uuid)
    start_time = Column(DateTime, default=datetime.now(timezone(timedelta(hours=3))))
    end_time = Column(DateTime, default=None)
    total_time = Column(String, default=None)
    photo = Column(String)
    user_id = Column(BigInteger, ForeignKey('Users.id', name='user_id'))
    user_geo = Column(String)
    distance_facility_user = Column(Integer)
    user = relationship('UserModel', back_populates='shifts')
    facility_id = Column(String)


class FacilityModel(base):
    __tablename__ = 'Facilities'
    id = Column(String, primary_key=True, default=get_uuid)
    name = Column(String)
    geo = Column(String)
    city = Column(String)
    access_get_range = Column(Integer)
    work_start_time = Column(Time)
    work_end_time = Column(Time)


class QuestionModel(base):
    __tablename__ = 'Questions'
    id = Column(String, primary_key=True, default=get_uuid)
    from_user_id = Column(BigInteger, ForeignKey('Users.id', name='user_id'))
    date = Column(DateTime, default=datetime.now(timezone(timedelta(hours=3))))
    content = Column(Text)
    tg_info = Column(PickleType, default={})
    users = relationship('UserModel', back_populates='questions')


class ReportModel(base):
    __tablename__ = 'Reports'
    id = Column(String, primary_key=True, default=get_uuid)
    is_monthly = Column(Boolean, default=False)
    user_id = Column(BigInteger, ForeignKey('Users.id', name='user_id'))
    user_name = Column(String)
    date_range = Column(String)
    users = relationship('UserModel', back_populates='reports')
    file = Column(String)


class LogModel(base):
    __tablename__ = 'Loggers'
    id = Column(String, primary_key=True, default=get_uuid)
    file = Column(String)
