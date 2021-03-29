from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from api.models.courier import Courier
from api.models.order import Order
from api.schemas.order import (
    OrdersPostRequest,
    OrdersAssignPostRequest,
    OrdersCompletePostRequest,
    ORDERS_RESPONSE,
    ASSIGN_ORDER_RESPONSE,
    COMPLETE_ORDER_RESPONSE,
)
from api.serializers.order import OrdersSerializer


class OrdersView(APIView):
    @swagger_auto_schema(
        request_body=OrdersPostRequest(many=True),
        responses=ORDERS_RESPONSE,
        operation_summary="Import orders",
        tags=["Orders"],
    )
    def post(self, request, format=None):
        data = request.data
        errors = []
        success = []

        for order in data:
            try:
                serializer = OrdersSerializer(data=order)
                if serializer.is_valid():
                    serializer.save()
                    success.append({"id": order.get("order_id")})
                else:
                    errors.append({"id": order.get("order_id")})
            except Exception as exc:
                errors.append({"id": order.get("order_id")})

        if errors:
            return Response(
                {"validation_error": {"orders": errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"orders": success}, status=status.HTTP_201_CREATED)


class OrderAssignView(APIView):
    @swagger_auto_schema(
        request_body=OrdersAssignPostRequest(),
        responses=ASSIGN_ORDER_RESPONSE,
        operation_summary="Assign orders to a courier by id",
        tags=["Orders"],
    )
    def post(self, request, format=None):
        courier_id = request.data.get("courier_id")
        courier = (
            Courier.objects.filter(id=courier_id)
            .prefetch_related("working_hours")
            .first()
        )
        if courier is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        success, assign_time = courier.get_not_delivered_orders()
        if success is not None:
            if success != list():
                return Response(
                    {"orders": success, "assign_time": assign_time},
                    status=status.HTTP_200_OK,
                )
            return Response({"orders": success}, status=status.HTTP_200_OK)

        weight = courier.type.weight
        orders = (
            Order.objects.filter(
                courier_id__isnull=True,
                region__in=courier.regions_id,
                weight__lte=weight,
            )
            .prefetch_related("delivery_hours")
            .all()
        )
        success, assign_time = courier.assign_orders(weight=weight, orders=orders)

        if success != list():
            return Response(
                {"orders": success, "assign_time": assign_time},
                status=status.HTTP_200_OK,
            )
        return Response({"orders": success}, status=status.HTTP_200_OK)


class OrderCompleteView(APIView):
    @swagger_auto_schema(
        request_body=OrdersCompletePostRequest(),
        responses=COMPLETE_ORDER_RESPONSE,
        operation_summary="Marks orders as completed",
        tags=["Orders"],
    )
    def post(self, request, format=None):
        courier_id = request.data.get("courier_id")
        order_id = request.data.get("order_id")
        complete_time = request.data.get("complete_time")
        order = Order.objects.filter(id=order_id, courier_id=courier_id).first()
        if order is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not order.is_delivered:
            order.is_delivered = True
            order.complete_time = complete_time
            order.courier_price = 500 * order.courier.type.coefficient
            order.save()

        return Response({"order_id": order_id}, status=status.HTTP_200_OK)
