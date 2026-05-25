from proto import seckill_pb2
from models.seckill import Order, Seckill
from typing import List
import json


class ProtobufResponseHandler():
    def _generate_seckill_detail_message(self, seckill_obj: Seckill):
        product = seckill_pb2.Product(
            id=seckill_obj.product.id,
            title=seckill_obj.product.title,
            price=int(seckill_obj.product.price),
            covers=json.dumps(seckill_obj.product.covers),
            detail=seckill_obj.product.detail or "",
            created_at=str(seckill_obj.product.created_at),
        )
        seckill = seckill_pb2.Seckill(
            id=seckill_obj.id,
            seckill_price=int(seckill_obj.seckill_price),
            starts_at=str(seckill_obj.starts_at),
            ends_at=str(seckill_obj.ends_at),
            created_at=str(seckill_obj.created_at),
            stock=seckill_obj.stock,
            max_per_buyer=seckill_obj.max_per_buyer,
            product=product,
        )

        return seckill

    def generate_seckill_detail_response(self, seckill_obj: Seckill):
        seckill = self._generate_seckill_detail_message(seckill_obj)

        response = seckill_pb2.GetSeckillDetailResponse(seckill=seckill)
        return response

    def generate_seckill_list_response(self, seckill_objs: List[Seckill]):
        seckills = []

        for seckill_obj in seckill_objs:
            seckill = self._generate_seckill_detail_message(seckill_obj)
            seckills.append(seckill)

        response = seckill_pb2.GetSeckillListResponse(seckills=seckills)
        return response

    def _generate_order_detail_message(self, order_obj: Order):
        seckill = self._generate_seckill_detail_message(order_obj.seckill)
        order = seckill_pb2.Order(
            id=order_obj.id,
            quantity=order_obj.quantity,
            amount=int(order_obj.amount),
            status=order_obj.status,
            created_at=str(order_obj.created_at),
            address=order_obj.address,
            seckill=seckill,
        )

        return order

    def generate_order_list_response(self, order_objs: List[Order]):
        orders = []

        for order_obj in order_objs:
            order = self._generate_order_detail_message(order_obj)
            orders.append(order)

        response = seckill_pb2.GetOrderListResponse(orders=orders)
        return response

response_handler = ProtobufResponseHandler()