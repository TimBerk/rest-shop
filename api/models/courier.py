from django.db import models
from django.utils.timezone import now


class CourierType(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    weight = models.IntegerField("Вес")
    coefficient = models.IntegerField("Коэффициент")

    class Meta:
        verbose_name = "Тип курьера"
        verbose_name_plural = "Типы курьера"

    def __str__(self):
        return self.id


class Courier(models.Model):
    NULL_ORDER_DATA = {"courier_id": None, "assign_time": None}

    type = models.ForeignKey(
        CourierType,
        on_delete=models.SET_NULL,
        related_name="courier",
        verbose_name="Тип",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Курьер"
        verbose_name_plural = "Курьеры"

    def __str__(self):
        return f"{self.type_id} {str(self.id)}"

    @property
    def regions_id(self):
        return list(self.regions.values_list("region_id", flat=True))

    @property
    def list_hours(self):
        return [obj.time_to_str_dict() for obj in self.working_hours.all()]

    @property
    def rating(self):
        regions_mean = []
        for region in self.regions.all():
            region_mean = []
            times = self.orders.filter(is_delivered=True, region=region.region_id).all()
            times_len = len(times)
            for i in range(times_len):
                if i == 0:
                    value = times[i].complete_time - times[i].assign_time
                else:
                    value = times[i].complete_time - times[i - 1].complete_time
                region_mean.append(value.seconds)
            if times_len:
                regions_mean.append(sum(region_mean) / times_len)

        if regions_mean == list():
            return None

        t = min(regions_mean)
        rating = (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5
        return round(rating, 2)

    def need_change_order_weight(self, courier_type):
        need_change = {"car": ["foot", "bike"], "bike": ["foot"]}
        return courier_type in need_change.get(str(self.type_id), [])

    def get_not_delivered_orders(self):
        orders = self.orders.filter(is_delivered=False).all()
        if orders:
            assign_time = orders[0].assign_time
            orders = [{"id": item.pk} for item in orders]
            return orders, assign_time
        return None, None

    def assign_orders(self, weight, orders):
        assign_time = now()
        success = []

        for work_time in self.working_hours.all():
            for order in orders:
                if weight == 0:
                    break

                if order.pk in success or order.weight > weight:
                    continue

                for delivery in order.delivery_hours.all():
                    check_start_time = (
                        work_time.time_from <= delivery.time_from < work_time.time_to
                    )
                    check_end_time = (
                        work_time.time_from < delivery.time_to <= work_time.time_to
                    )
                    if check_start_time or check_end_time:
                        order.courier_id = self.pk
                        order.assign_time = assign_time
                        order.save()
                        success.append(order.id)
                        weight -= order.weight
                        break
        success = sorted(success)
        return [{"id": item} for item in success], assign_time

    def check_orders(self):
        delivered = []
        for order in self.orders.filter(is_delivered=False).all():
            for work_time in self.working_hours.all():
                for delivery in order.delivery_hours.all():
                    check_start_time = (
                        work_time.time_from <= delivery.time_from < work_time.time_to
                    )
                    check_end_time = (
                        work_time.time_from < delivery.time_to <= work_time.time_to
                    )
                    if check_start_time or check_end_time:
                        delivered.append(order.id)
                        break

            if order.pk not in delivered:
                order.courier_id = None
                order.assign_time = None
                order.save()


class CourierRegion(models.Model):
    courier = models.ForeignKey(
        Courier, related_name="regions", on_delete=models.CASCADE
    )
    region_id = models.IntegerField("Регион")

    class Meta:
        verbose_name = "Регион курьера"
        verbose_name_plural = "Регионы курьера"


class CourierWork(models.Model):
    courier = models.ForeignKey(
        Courier, related_name="working_hours", on_delete=models.CASCADE
    )
    time_from = models.TimeField("Время с", null=True)
    time_to = models.TimeField("Время по", null=True)

    class Meta:
        verbose_name = "Время работы курьера"
        verbose_name_plural = "Периоды работы курьера"

    def __str__(self):
        return f"{self.time_from.strftime('%H:%M')}-{self.time_to.strftime('%H:%M')}"

    def time_to_str_dict(self):
        return {
            "time_from": self.time_from.strftime("%H:%M"),
            "time_to": self.time_to.strftime("%H:%M"),
        }
