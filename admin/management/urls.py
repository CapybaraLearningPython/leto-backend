from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewset,
    SeckillViewset,
    OrderViewset,
    health_check,
    UserLoginStatusHandler,
)
from django.urls import path

router = DefaultRouter()
router.register("product", ProductViewset, basename="product")
router.register("seckill", SeckillViewset, basename="seckill")
router.register("order", OrderViewset, basename="order")

app_name = "management"
urlpatterns = [
    path("health_check/", health_check, name="health_check"),
    path(
        "user_login_status/", UserLoginStatusHandler.as_view(), name="user_login_status"
    ),
] + router.urls
