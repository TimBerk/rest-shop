from django.urls import include, path

from api.views import courier, order
from rest_framework.routers import DefaultRouter
from .yasg import urlpatterns as doc_urls

app_name = "api"
router = DefaultRouter()


urlpatterns = [
    path("couriers", courier.CouriersView.as_view(), name="couriers"),
    path("couriers/<courier_id>", courier.CourierView.as_view(), name="courier_edit"),
    path("orders", order.OrdersView.as_view(), name="orders"),
    path("orders/assign", order.OrderAssignView.as_view(), name="order_assign"),
    path("orders/complete", order.OrderCompleteView.as_view(), name="order_complete"),
]

urlpatterns += doc_urls
urlpatterns += (path("", include(router.urls)),)
