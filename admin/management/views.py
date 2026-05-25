from rest_framework.viewsets import ModelViewSet
from .models import Product, Seckill, Order
from .serializers import ProductsSerializer, SeckillSerializer, OrderSerializer
from django.http import JsonResponse
from .utils.cache import redis_client
from django.db import IntegrityError
from django.db.models import ProtectedError
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response


class ProductViewset(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductsSerializer

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError("Foreign key constraint")
        except IntegrityError:
            raise ValidationError("Foreign key constraint")


class SeckillViewset(ModelViewSet):
    queryset = Seckill.objects.all()
    serializer_class = SeckillSerializer
    SECKILL_KEY = SECKILL_KEY = "seckill_{}"

    def perform_create(self, serializer):
        redis_client.set_seckill_cache(serializer)

    def perform_update(self, serializer):
        redis_client.set_seckill_cache(serializer)

    def perform_destroy(self, instance):
        seckill_serializer = self.serializer_class(instance)
        redis_client.delete_seckill_cache(seckill_serializer)
        super().perform_destroy(instance)


class OrderViewset(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class UserLoginStatusHandler(APIView):
    USER_KEY = "refresh_token_{}"

    def get(self, request):
        cursor = 0
        user_ids = []

        while True:
            cursor, batch = redis_client.client.scan(
                cursor=cursor, match="refresh_token_*", count=1000
            )
            user_ids.extend([k.split("_")[-1] for k in batch])

            if cursor == 0:
                break

        return Response(data={"user_ids": user_ids})
    
    def post(self, request):
        user_ids = request.data.get("user_ids")
        keys = [self.USER_KEY.format(user_id) for user_id in user_ids]
        for key in keys:
            redis_client.client.delete(key)

        return Response(data={"message": "Logout successfully"})



# Health check
def health_check(request):
    return JsonResponse({"status": "ok"})
