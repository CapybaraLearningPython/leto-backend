from . import Base
from sqlalchemy import Column, String, BigInteger, Boolean
from utils.snowflake.snowflake import Snowflake
from sqlalchemy_serializer import SerializerMixin
import settings
import random

snowflake = Snowflake(settings.DATA_CENTER_ID, settings.WORKER_ID)

def generate_id():
    id = snowflake.get_id()
    return id

def generate_username():
    return f"乐购星人{random.randint(0, 9999):04d}"

class User(Base, SerializerMixin):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, default=generate_id)
    tel = Column(String(20), unique=True, index=True)
    username = Column(String(20), default='乐购星人')
    avatar = Column(String(200))
    is_seller = Column(Boolean, default=False)