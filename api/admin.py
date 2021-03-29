from django.contrib import admin

from api.models import courier, order


@admin.register(courier.CourierType)
class CourierTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "weight",
        "coefficient",
    )
    list_display_links = ("id",)
    search_fields = ("weight",)
    ordering = ("id",)


class CourierRegionAdmin(admin.TabularInline):
    model = courier.CourierRegion
    extra = 0
    readonly_fields = ["courier_id"]


class CourierWorkAdmin(admin.TabularInline):
    model = courier.CourierWork
    extra = 0
    readonly_fields = ["courier_id"]


@admin.register(courier.Courier)
class Courier(admin.ModelAdmin):
    inlines = [CourierRegionAdmin, CourierWorkAdmin]
    list_filter = ("type",)
    list_display = (
        "id",
        "type",
    )
    list_display_links = ("id",)
    search_fields = ("id",)
    ordering = ("id",)


class OrderDeliveryWorkAdmin(admin.TabularInline):
    model = order.OrderDelivery
    extra = 0
    readonly_fields = ["order_id"]


@admin.register(order.Order)
class Order(admin.ModelAdmin):
    inlines = [OrderDeliveryWorkAdmin]
    list_filter = ("is_delivered",)
    list_display = (
        "id",
        "region",
        "weight",
        "is_delivered",
        "assign_time",
        "complete_time",
    )
    list_display_links = ("id",)
    search_fields = ("id", "weight")
    ordering = ("id",)
