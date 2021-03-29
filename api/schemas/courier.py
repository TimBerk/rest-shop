from drf_yasg import openapi
from rest_framework import serializers

COURIER_PARAM = openapi.Parameter(
    name="courier_id",
    description="Id courier",
    in_=openapi.IN_PATH,
    type=openapi.TYPE_INTEGER,
)

COURIER_TYPE = ["foot", "bike", "car"]


class CouriersIdSchema(serializers.Serializer):
    id = serializers.IntegerField(label="Уникальный идентификатор курьера")


class CourierItem(serializers.Serializer):
    courier_id = serializers.IntegerField(label="Уникальный идентификатор курьера")
    courier_type = serializers.ChoiceField(label="Тип курьера", choices=COURIER_TYPE)
    regions = serializers.ListSerializer(
        label="Список идентификаторов районов", child=serializers.IntegerField()
    )
    working_hours = serializers.ListSerializer(
        label="График работы курьера", child=serializers.CharField()
    )


class CouriersPostRequest(serializers.Serializer):
    data = CourierItem(many=True)


class CouriersIds(serializers.Serializer):
    couriers = CouriersIdSchema(many=True)


class CouriersIdsAP(serializers.Serializer):
    validation_error = CouriersIds()


class CourierGetResponse(serializers.Serializer):
    courier_id = serializers.IntegerField(label="Уникальный идентификатор курьера")
    courier_type = serializers.ChoiceField(label="Тип курьера", choices=COURIER_TYPE)
    regions = serializers.ListSerializer(
        label="Список идентификаторов районов", child=serializers.IntegerField()
    )
    working_hours = serializers.ListSerializer(
        label="График работы курьера", child=serializers.CharField()
    )
    rating = serializers.FloatField(label="Рейтинг", required=False)
    earnings = serializers.IntegerField(label="Заработок")


class CourierUpdateRequest(serializers.Serializer):
    courier_type = serializers.ChoiceField(label="Тип курьера", choices=COURIER_TYPE)
    regions = serializers.ListSerializer(
        label="Список идентификаторов районов", child=serializers.IntegerField()
    )
    working_hours = serializers.ListSerializer(
        label="График работы курьера", child=serializers.CharField()
    )


COURIERS_RESPONSE = {
    "201": openapi.Response(description="Created", schema=CouriersIds(many=True)),
    "400": openapi.Response(description="Bad request", schema=CouriersIdsAP()),
}

COURIER_PATCH_RESPONSE = {
    "200": openapi.Response(description="Created", schema=CourierItem()),
    "400": openapi.Response(description="Bad request"),
    "404": openapi.Response(description="Not found"),
}

COURIER_GET_RESPONSE = {
    "200": openapi.Response(description="OK", schema=CourierGetResponse()),
    "404": openapi.Response(description="Not found"),
}
