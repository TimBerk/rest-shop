from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models.order import Order


class OrderAssignTests(APITestCase):
    fixtures = [
        "api/fixtures/courier_type.json",
        "api/tests/fixtures/couriers.json",
        "api/tests/fixtures/orders.json",
    ]

    def setUp(self):
        self.valid_payload = {"courier_id": 2}
        self.invalid_payload = {"courier_id": 5}
        self.complete_payload = {
            "courier_id": 2,
            "order_id": 3,
            "complete_time": "2021-01-10T10:33:01.42Z",
        }
        self.url = reverse("api:order_assign")
        self.complete_url = reverse("api:order_complete")

    def test_response_valid(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_invalid(self):
        response = self.client.post(self.url, self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_time_in_not_delivered_orders(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        assign_time = response.json().get("assign_time")

        response = self.client.post(self.url, self.valid_payload, format="json")
        assign_time_2 = response.json().get("assign_time")

        self.assertEqual(assign_time, assign_time_2)

    def test_empty_orders_in_response(self):
        self.client.post(self.url, self.valid_payload, format="json")
        self.client.post(self.complete_url, self.complete_payload, format="json")

        response = self.client.post(self.url, self.valid_payload, format="json")
        orders = response.json().get("orders")
        self.assertEqual(orders, [])

    def test_empty_orders_in_db(self):
        self.client.post(self.url, self.valid_payload, format="json")
        self.client.post(self.complete_url, self.complete_payload, format="json")
        self.client.post(self.url, self.valid_payload, format="json")

        orders = Order.objects.filter(
            is_delivered=False, courier_id__isnull=True, region=22
        ).count()
        self.assertEqual(orders, 0)


class OrderAssignTimeTests(APITestCase):
    fixtures = [
        "api/fixtures/courier_type.json",
        "api/tests/fixtures/couriers.json",
        "api/tests/fixtures/orders_assign_time.json",
    ]

    def setUp(self):
        self.url = reverse("api:order_assign")
        self.first_courier = {"courier_id": 1}
        self.third_courier = {"courier_id": 3}

    def test_id_count_in_response(self):
        response = self.client.post(self.url, self.first_courier, format="json")
        content = response.json()
        self.assertEqual(len(content.get("orders")), 3)

    def test_id_in_response(self):
        response = self.client.post(self.url, self.first_courier, format="json")
        content = response.json()
        orders_id = [item.get("id") for item in content.get("orders")]
        self.assertEqual(orders_id, [1, 3, 4])

    def test_orders_count_for_courier_in_db(self):
        response = self.client.post(self.url, self.first_courier, format="json")
        content = response.json()
        orders_id = [item.get("id") for item in content.get("orders")]
        orders_count = Order.objects.filter(courier_id=1, id__in=orders_id).count()
        self.assertEqual(orders_count, 3)

    def test_orders_count_without_courier_in_db(self):
        response = self.client.post(self.url, self.first_courier, format="json")
        content = response.json()
        orders_id = [item.get("id") for item in content.get("orders")]
        orders_count = Order.objects.exclude(id__in=orders_id).count()
        self.assertEqual(orders_count, 2)

    def test_orders_empty_in_response(self):
        response = self.client.post(self.url, self.third_courier, format="json")
        content = response.json()
        self.assertEqual(len(content.get("orders")), 0)


class OrderAssignWeightTests(APITestCase):
    fixtures = [
        "api/fixtures/courier_type.json",
        "api/tests/fixtures/couriers.json",
        "api/tests/fixtures/orders_assign_weight.json",
    ]

    def setUp(self):
        self.url = reverse("api:order_assign")
        self.first_courier = {"courier_id": 1}
        self.second_courier = {"courier_id": 2}
        self.third_courier = {"courier_id": 3}

    def test_response(self):
        response = self.client.post(self.url, self.first_courier, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_id_count_in_response(self):
        response = self.client.post(self.url, self.first_courier, format="json")
        content = response.json()
        self.assertEqual(len(content.get("orders")), 2)

    def test_id_in_response(self):
        response = self.client.post(self.url, self.first_courier, format="json")
        content = response.json()
        orders_id = [item.get("id") for item in content.get("orders")]
        self.assertEqual(orders_id, [1, 4])

    def test_orders_count_for_courier_in_db(self):
        response = self.client.post(self.url, self.first_courier, format="json")
        content = response.json()
        orders_id = [item.get("id") for item in content.get("orders")]
        orders_count = Order.objects.filter(courier_id=1, id__in=orders_id).count()
        self.assertEqual(orders_count, 2)

    def test_orders_count_without_courier_in_db(self):
        response = self.client.post(self.url, self.first_courier, format="json")
        content = response.json()
        orders_id = [item.get("id") for item in content.get("orders")]
        orders_count = Order.objects.exclude(id__in=orders_id).count()
        self.assertEqual(orders_count, 3)

    def test_orders_count_unchanged_after_several_couriers(self):
        self.client.post(self.url, self.first_courier, format="json")
        self.client.post(self.url, self.second_courier, format="json")
        self.client.post(self.url, self.third_courier, format="json")
        orders_count = Order.objects.filter(courier_id__isnull=True).count()
        self.assertEqual(orders_count, 2)
