from datetime import datetime

from django.db import transaction
from django.db.models import Sum
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models.courier import Courier, CourierType, CourierWork, CourierRegion
from api.models.order import Order


class WorkingHoursField(serializers.CharField):
    def to_representation(self, value):
        time_to = value.time_to.strftime("%H:%M")
        time_from = value.time_from.strftime("%H:%M")
        return f"{time_from}-{time_to}"

    def to_internal_value(self, data):
        periods = data.split("-")
        if len(periods) < 2:
            raise ValidationError()
        try:
            time1 = datetime.strptime(periods[0], "%H:%M")
            time2 = datetime.strptime(periods[1], "%H:%M")

            if time1 > time2:
                raise ValidationError()
        except ValueError:
            raise ValidationError()
        return {"time_from": periods[0], "time_to": periods[1]}


class RegionField(serializers.IntegerField):
    def to_representation(self, value):
        return value.region_id


class CourierSerializer(serializers.ModelSerializer):
    courier_id = serializers.IntegerField(source="id")
    courier_type = serializers.PrimaryKeyRelatedField(
        queryset=CourierType.objects.all(), source="type"
    )
    regions = serializers.ListSerializer(child=serializers.IntegerField())
    working_hours = serializers.ListSerializer(child=WorkingHoursField())

    class Meta:
        model = Courier
        fields = ("courier_id", "courier_type", "regions", "working_hours")

    def validate(self, data):
        if hasattr(self, "initial_data"):
            unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())
            if unknown_keys:
                raise ValidationError()
        return data

    def create(self, validated_data):
        regions_data = validated_data.pop("regions", None)
        working_hours_data = validated_data.pop("working_hours", [])

        with transaction.atomic():
            courier = self.Meta.model.objects.create(**validated_data)

            for each in regions_data:
                CourierRegion.objects.create(
                    **{"region_id": each, "courier_id": courier.pk}
                )

            for each in working_hours_data:
                each["courier_id"] = courier.pk
                CourierWork.objects.create(**each)

        return courier


class CourierUpdateSerializer(serializers.ModelSerializer):
    courier_id = serializers.IntegerField(source="id", required=False)
    courier_type = serializers.PrimaryKeyRelatedField(
        queryset=CourierType.objects.all(), source="type", required=False
    )
    regions = serializers.ListSerializer(child=RegionField(), required=False)
    working_hours = serializers.ListSerializer(
        child=WorkingHoursField(), required=False
    )

    class Meta:
        model = Courier
        fields = ("courier_id", "courier_type", "regions", "working_hours")
        read_only_fields = ("courier_id",)
        write_only_fields = (
            "courier_type",
            "regions",
            "working_hours",
        )

    def validate(self, data):
        if hasattr(self, "initial_data"):
            unknown_keys = set(self.initial_data.keys()) - set(
                self.Meta.write_only_fields
            )
            if unknown_keys:
                raise ValidationError()
        return data

    def update(self, instance, validated_data):
        region_ids = instance.regions_id
        regions_data = validated_data.pop("regions", region_ids)

        courier_type = instance.type
        type_data = validated_data.pop("type", courier_type)

        working_hours = instance.list_hours
        working_hours_data = validated_data.pop("working_hours", working_hours)

        if regions_data != region_ids:
            region_add = set(regions_data) - set(region_ids)
            region_delete = list(set(region_ids) - set(regions_data))
            if region_add:
                regions = [
                    CourierRegion(courier=instance, region_id=param)
                    for param in region_add
                ]
                CourierRegion.objects.bulk_create(regions)
            if region_delete:
                Order.objects.filter(
                    courier_id=instance.pk, is_delivered=False, region__in=region_delete
                ).update(**instance.NULL_ORDER_DATA)
                CourierRegion.objects.filter(
                    courier_id=instance.pk, region_id__in=region_delete
                ).delete()
            instance.refresh_from_db()

        if type_data != courier_type and instance.need_change_order_weight(
            type_data.pk
        ):
            weight = CourierType.objects.filter(id=type_data.pk).first().weight
            for order in instance.orders.filter(is_delivered=False).all():
                if order.weight > weight:
                    order.courier_id = None
                    order.assign_time = None
                    order.save()
                else:
                    weight -= order.weight
            instance.refresh_from_db()
        if type_data != courier_type:
            instance.type = type_data
            instance.save()

        if working_hours_data != working_hours:
            hours_add = [x for x in working_hours_data if x not in working_hours]
            hours_delete = [x for x in working_hours if x not in working_hours_data]

            if working_hours_data == list():
                Order.objects.filter(courier_id=instance.pk, is_delivered=False).update(
                    **instance.NULL_ORDER_DATA
                )
                CourierWork.objects.filter(courier_id=instance.pk).delete()
            else:
                if hours_delete:
                    for work_time in hours_delete:
                        CourierWork.objects.filter(
                            courier_id=instance.pk,
                            time_from=work_time.get("time_from"),
                            time_to=work_time.get("time_to"),
                        ).delete()
                if hours_add:
                    for each in hours_add:
                        each["courier_id"] = instance.pk
                        CourierWork.objects.create(**each)

        instance.check_orders()
        instance.refresh_from_db()
        return instance


class CourierRetrieveSerializer(serializers.ModelSerializer):
    courier_id = serializers.IntegerField(source="id")
    courier_type = serializers.PrimaryKeyRelatedField(
        queryset=CourierType.objects.all(), source="type"
    )
    regions = serializers.ListSerializer(child=RegionField())
    working_hours = serializers.ListSerializer(child=WorkingHoursField())
    rating = serializers.FloatField()
    earnings = serializers.SerializerMethodField(method_name="get_earnings")

    def get_earnings(self, obj):
        sum = obj.orders.filter(is_delivered=True).aggregate(Sum("courier_price"))[
            "courier_price__sum"
        ]
        return sum if sum else 0

    class Meta:
        model = Courier
        fields = (
            "courier_id",
            "courier_type",
            "regions",
            "working_hours",
            "rating",
            "earnings",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for field in self.fields:
            if representation[field] is None:
                representation.pop(field)
        return representation
