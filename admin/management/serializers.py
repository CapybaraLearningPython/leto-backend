from rest_framework.serializers import (
    ModelSerializer,
    BigIntegerField,
    ValidationError,
    CharField
)
from .models import Product, Seckill, Order


class ProductsSerializer(ModelSerializer):
    id = CharField(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SeckillSerializer(ModelSerializer):
    product = ProductsSerializer(read_only=True)
    product_id = BigIntegerField(write_only=True)
    id = CharField(read_only=True)

    class Meta:
        model = Seckill
        exclude = ["version_id"]
        read_only_fields = ["id", "created_at", "product"]

    def create(self, validated_data):
        product_id = validated_data.pop("product_id")
        product = Product.objects.filter(id=product_id).first()

        if not product:
            raise ValidationError("找不到对应的商品！")

        validated_data["product"] = product

        return super().create(validated_data)


class OrderSerializer(ModelSerializer):
    seckill = SeckillSerializer(read_only=True)
    user_id = BigIntegerField(read_only=True)
    id = CharField(read_only=True)
    user_id = CharField(read_only=True)

    class Meta:
        model = Order
        exclude = ["order_str"]
        read_only_fields = [
            "id",
            "quantity",
            "amount",
            "status",
            "created_at",
            "seckill",
            "user_id",
        ]
