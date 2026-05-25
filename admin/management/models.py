from django.db import models
from .utils.snowflake.snowflake import Snowflake
from django.conf import settings
import uuid

snowflake = Snowflake(settings.DATA_CENTER_ID, settings.WORKER_ID)

def generate_id():
    return snowflake.get_id()

def generate_version_id():
    return uuid.uuid4().hex

class Order(models.Model):
    id = models.BigAutoField(primary_key=True, default=generate_id)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    seckill = models.ForeignKey('Seckill', on_delete=models.DO_NOTHING)
    user_id = models.BigIntegerField()
    order_str = models.TextField()
    address = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'order'
        unique_together = (('user_id', 'seckill'),)


class Product(models.Model):
    id = models.BigAutoField(primary_key=True, default=generate_id)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    covers = models.JSONField(blank=True, null=True)
    detail = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'product'
        ordering = ['-created_at']


class Seckill(models.Model):
    id = models.BigAutoField(primary_key=True, default=generate_id)
    seckill_price = models.DecimalField(max_digits=10, decimal_places=2)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    stock = models.IntegerField()
    max_per_buyer = models.IntegerField(blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    version_id = models.CharField(max_length=100, default=generate_version_id)

    class Meta:
        managed=False
        db_table = 'seckill'
        ordering = ['-created_at']
