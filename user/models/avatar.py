from . import Base
from sqlalchemy import Column, String, BigInteger
from utils.snowflake.snowflake import Snowflake
from sqlalchemy_serializer import SerializerMixin
import settings

def generate_id():
    id = Snowflake(settings.DATA_CENTER_ID, settings.WORKER_ID).get_id()
    return id

class Avatar(Base, SerializerMixin):
    __tablename__ = "avatar"
    serialize_only = ["id", "url", "user_id"]
    id = Column(BigInteger, primary_key=True, default=generate_id)
    url = Column(String(200), nullable=False)
    
    user_id = Column(BigInteger, nullable=False, unique=True)