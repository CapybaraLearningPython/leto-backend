from alipay import AliPay
from alipay.utils import AliPayConfig
import aiofiles
import settings
from models.seckill import Order
from utils.single import SingletonMeta


class AliPayClient(metaclass=SingletonMeta):
    def __init__(self):
        self.client = None

    async def _init_client(self):
        if self.client is None:
            self.client = await self._get_client()

    async def _get_app_private_key_string(self, path: str):
        async with aiofiles.open(path, mode="r") as f:
            app_private_key_string = await f.read()
            self.app_private_key_string = app_private_key_string

    async def _get_alipay_public_key_string(self, path: str):
        async with aiofiles.open(path, mode="r") as f:
            alipay_public_key_string = await f.read()
            self.alipay_public_key_string = alipay_public_key_string

    async def _get_client(self):
        await self._get_app_private_key_string("keys/app_private.key")
        await self._get_alipay_public_key_string("keys/alipay_public.pem")

        _alipay = AliPay(
            appid=settings.ALIPAY_APP_ID,
            app_notify_url=settings.ALIPAY_NOTIFY_URL,
            app_private_key_string=self.app_private_key_string,
            alipay_public_key_string=self.alipay_public_key_string,
            sign_type="RSA2",
            debug=True,
            verbose=True,
            config=AliPayConfig(timeout=15),
        )
        return _alipay

    async def get_order_string(self, order: Order, title: str):
        await self._init_client()
        order_string = self.client.api_alipay_trade_page_pay(
            out_trade_no=str(order.id),
            total_amount=float(order.amount / 100),
            subject=title,
            return_url=settings.ALIPAY_RETURN_URL,
        )
        pay_url = f"{settings.ALIPAY_BASE_URL}?{order_string}"
        return pay_url

    async def verify(self, data, sign):
        await self._init_client()
        return self.client.verify(data, sign)


alipay_client = AliPayClient()
