from . import Base
from sqlalchemy import Column, String, BigInteger, Boolean
from utils.snowflake.snowflake import Snowflake
from sqlalchemy_serializer import SerializerMixin
import settings
from utils.snowflake.snowflake import Snowflake

snowflake = Snowflake(settings.DATA_CENTER_ID, settings.WORKER_ID)
def generate_id():
    id = snowflake.get_id()
    return id

class Address(Base, SerializerMixin):
    __tablename__ = 'address'

    serialize_only = ['id', 'name', 'tel', 'region', 'detail']
    id = Column(BigInteger, primary_key=True, default=generate_id)
    name = Column(String(20), nullable=False)
    tel = Column(String(20), nullable=False)
    region = Column(String(200), nullable=False)
    detail = Column(String(200), nullable=False)

    user_id = Column(BigInteger, nullable=False)