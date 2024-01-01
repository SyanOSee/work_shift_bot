# Third-party
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import PickleType
from sqlalchemy.orm import relationship


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
    complain = Column(String, default='')
    current_facility_id = Column(String, default=None)
    shifts = relationship('ShiftModel', back_populates='user')
    income = Column(Float, default=0)
    hours = Column(Float, default=0)
    last_month_income = Column(Float, default=0)
    last_month_hours = Column(Float, default=0)
    rate_an_hour = Column(Float, default=0)


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
    facility_id = Column(String, ForeignKey('Facilities.id', name='facility_id'))


class FacilityModel(base):
    __tablename__ = 'Facilities'
    id = Column(String, primary_key=True, default=get_uuid)
    name = Column(String, unique=True)
    geo = Column(String, unique=True)
    city = Column(String)
    access_get_range = Column(Integer)
    work_start_time = Column(Time)
    work_end_time = Column(Time)


class QuestionModel(base):
    __tablename__ = 'Questions'
    id = Column(String, primary_key=True, default=get_uuid)
    user_name = Column(String)
    from_user_id = Column(BigInteger)
    is_closed = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.now(timezone(timedelta(hours=3))))
    close_date = Column(DateTime, default=None)
    content = Column(Text)
    tg_info = Column(PickleType, default={})


class ReportModel(base):
    __tablename__ = 'Reports'
    id = Column(String, primary_key=True, default=get_uuid)
    is_monthly = Column(Boolean, default=False)
    user_id = Column(BigInteger, ForeignKey('Users.id', name='user_id'))
    user_name = Column(String)
    date_range = Column(String)
    file = Column(String)


class LogModel(base):
    __tablename__ = 'Loggers'
    id = Column(String, primary_key=True, default=get_uuid)
    file = Column(String)
