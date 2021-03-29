from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models.order import Order, OrderDelivery


class DeliveryHoursField(serializers.CharField):
    def to_representation(self, value):
        time_to = value.time_to.strftime("%H:%M")
        time_from = value.time_from.strftime("%H:%M")
        return f"{time_to}-{time_from}"

    def to_internal_value(self, data):
        periods = data.split("-")
        return OrderDelivery(time_from=periods[0], time_to=periods[1])


class OrdersSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="id", required=True)
    region = serializers.IntegerField(required=True)
    delivery_hours = serializers.ListSerializer(child=DeliveryHoursField())

    class Meta:
        model = Order
        fields = ("order_id", "weight", "region", "delivery_hours")

    def validate(self, data):
        if hasattr(self, "initial_data"):
            unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())
            if unknown_keys:
                raise ValidationError()
        return data

    def create(self, validated_data):
        delivery_hours_data = validated_data.pop("delivery_hours", [])

        with transaction.atomic():
            order = self.Meta.model.objects.create(**validated_data)

            for each in delivery_hours_data:
                each.order = order
                each.save()

        return order
