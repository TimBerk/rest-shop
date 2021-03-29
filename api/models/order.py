from django.db import models

from api.models.courier import Courier


class Order(models.Model):
    region = models.IntegerField("Регион")
    weight = models.DecimalField("Вес", max_digits=5, decimal_places=2)

    is_delivered = models.BooleanField("Доставлен", default=False)
    courier = models.ForeignKey(
        Courier,
        on_delete=models.SET_NULL,
        related_name="orders",
        verbose_name="Курьер",
        blank=True,
        null=True,
    )
    courier_price = models.DecimalField(
        "Оплата курьеру", default=0.00, max_digits=7, decimal_places=2
    )
    assign_time = models.DateTimeField("Время назначение", blank=True, null=True)
    complete_time = models.DateTimeField("Время завершение", blank=True, null=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderDelivery(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="delivery_hours",
        on_delete=models.CASCADE,
        verbose_name="Заказ",
    )
    time_from = models.TimeField("Время с", null=True)
    time_to = models.TimeField("Время по", null=True)

    class Meta:
        verbose_name = "Время доставки заказа"
        verbose_name_plural = "Периоды доставки заказа"
