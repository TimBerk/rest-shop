from drf_yasg import openapi
from rest_framework import serializers


class OrdersIdSchema(serializers.Serializer):
    id = serializers.IntegerField(label="Уникальный идентификатор курьера")


class OrderItem(serializers.Serializer):
    order_id = serializers.IntegerField(label="Уникальный идентификатор заказа")
    weight = serializers.DecimalField(
        label="Вес", max_digits=4, decimal_places=2, max_value=50, min_value=0.01
    )
    region = serializers.IntegerField(label="Список идентификаторов районов")
    delivery_hours = serializers.ListSerializer(
        label="Время доставки", child=serializers.CharField()
    )


class OrdersPostRequest(serializers.Serializer):
    data = OrderItem(many=True)


class OrdersIds(serializers.Serializer):
    orders = OrdersIdSchema(many=True)


class OrdersIdsAP(serializers.Serializer):
    validation_error = OrdersIds(required=True)


ORDERS_RESPONSE = {
    "201": openapi.Response(description="Created", schema=OrdersIds(many=True)),
    "400": openapi.Response(description="Bad request", schema=OrdersIdsAP()),
}


class AssignTime(serializers.Serializer):
    assign_time = serializers.DateTimeField(
        label="Время доставки", format="%Y-%m-%dT%H:%M:%SZ"
    )


class OrdersAssignPostRequest(serializers.Serializer):
    courier_id = serializers.IntegerField(label="Уникальный идентификатор курьера")


class OrdersAssignPostResponse(serializers.Serializer):
    orders = OrdersIdSchema(many=True)
    assign_time = serializers.DateTimeField(
        label="Время доставки", format="%Y-%m-%dT%H:%M:%SZ"
    )


class OrdersCompletePostRequest(serializers.Serializer):
    courier_id = serializers.IntegerField(label="Уникальный идентификатор курьера")


class OrdersCompletePostResponse(serializers.Serializer):
    courier_id = serializers.IntegerField(label="Уникальный идентификатор курьера")
    order_id = serializers.IntegerField(label="Уникальный идентификатор заказа")
    complete_time = serializers.DateTimeField(
        label="Время доставки", format="%Y-%m-%dT%H:%M:%SZ"
    )


ASSIGN_ORDER_RESPONSE = {
    "201": openapi.Response(description="OK", schema=OrdersAssignPostResponse),
    "400": openapi.Response(description="Bad request"),
}

COMPLETE_ORDER_RESPONSE = {
    "200": openapi.Response(description="OK", schema=OrdersCompletePostResponse()),
    "400": openapi.Response(description="Bad request"),
}
