from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models.order import Order


class OrdersTests(APITestCase):
    fixtures = ["api/fixtures/courier_type.json"]

    def setUp(self):
        self.valid_payload = [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"],
            },
            {
                "order_id": 2,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"],
            },
            {
                "order_id": 3,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"],
            },
        ]
        self.invalid_payload = [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"],
            },
            {
                "order_id": 1,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"],
            },
            {
                "order_id": 3,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"],
            },
        ]

    def test_valid_response(self):
        url = reverse("api:orders")
        response = self.client.post(url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_valid_orders_response(self):
        url = reverse("api:orders")
        valid_orders = [{"id": 1}, {"id": 2}, {"id": 3}]
        response = self.client.post(url, self.valid_payload, format="json")
        content = response.json()
        self.assertEqual(content.get("orders"), valid_orders)

    def test_valid_orders_db(self):
        url = reverse("api:orders")
        self.client.post(url, self.valid_payload, format="json")
        self.assertEqual(Order.objects.count(), 3)

    def test_invalid_response(self):
        url = reverse("api:orders")
        response = self.client.post(url, self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_orders_response(self):
        url = reverse("api:orders")
        invalid_orders = [{"id": 2}, {"id": 3}]
        response = self.client.post(url, self.invalid_payload, format="json")
        content = response.json()
        self.assertEqual(content.get("validation_error").get("orders"), invalid_orders)

    def test_invalid_orders_db(self):
        url = reverse("api:orders")
        self.client.post(url, self.invalid_payload, format="json")
        self.assertEqual(Order.objects.count(), 1)
