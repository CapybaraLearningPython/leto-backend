from models import Base
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Numeric,
    JSON,
    Text,
    DateTime,
    Integer,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from utils.snowflake.snowflake import Snowflake
from datetime import datetime
import uuid
import enum
import settings


class OrderStatusEnum(enum.Enum):
    PENDING_PAYMENT = 1
    PAID = 2


def generate_id():
    id = Snowflake(settings.DATA_CENTER_ID, settings.WORKER_ID).get_id()
    return id


class Product(Base, SerializerMixin):
    __tablename__ = "product"
    serialize_only = ["id", "title", "price", "covers", "detail", "created_at"]

    id = Column(BigInteger, primary_key=True, default=generate_id)
    title = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    covers = Column(JSON)
    detail = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    seckills = relationship("Seckill", back_populates="product", lazy="noload")


class Seckill(Base, SerializerMixin):
    __tablename__ = "seckill"
    serialize_only = [
        "id",
        "seckill_price",
        "starts_at",
        "ends_at",
        "created_at",
        "stock",
        "max_per_buyer",
        "product",
    ]

    id = Column(BigInteger, primary_key=True, default=generate_id)
    seckill_price = Column(Numeric(10, 2), nullable=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    stock = Column(Integer, nullable=False)
    max_per_buyer = Column(Integer)

    product = relationship(Product, back_populates="seckills", lazy="selectin")
    product_id = Column(BigInteger, ForeignKey("product.id"), nullable=False)
    orders = relationship("Order", back_populates="seckill", lazy="noload")

    version_id = Column(String(100), nullable=False)

    __mapper_args__ = {
        "version_id_col": version_id,
        "version_id_generator": lambda _: uuid.uuid4().hex,
    }


class Order(Base, SerializerMixin):
    __tablename__ = "order"
    serialize_only = [
        "id",
        "quantity",
        "amount",
        "status",
        "created_at",
        "address",
        "seckill",
    ]

    id = Column(BigInteger, primary_key=True, default=generate_id)
    quantity = Column(Integer, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Integer, nullable=False, default=OrderStatusEnum.PENDING_PAYMENT.value)
    created_at = Column(DateTime, default=datetime.now)
    order_str = Column(Text, nullable=False)
    address = Column(String(200), nullable=False)

    seckill_id = Column(BigInteger, ForeignKey("seckill.id"), nullable=False)
    seckill = relationship(Seckill, back_populates="orders", lazy="selectin")
    user_id = Column(BigInteger, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "seckill_id", name="uk_user_seckill"),
    )
