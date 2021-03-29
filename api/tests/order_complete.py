from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
from api.models.order import Order

fake = Faker()


class OrderCompleteTests(APITestCase):
    fixtures = [
        "api/fixtures/courier_type.json",
        "api/tests/fixtures/couriers.json",
        "api/tests/fixtures/orders.json",
    ]

    def setUp(self):
        self.valid_payload = {
            "courier_id": 2,
            "order_id": 3,
            "complete_time": "2021-01-10T10:33:01.42Z",
        }
        self.invalid_payload = {
            "courier_id": 5,
            "order_id": 3,
            "complete_time": "2021-01-10T10:33:01.42Z",
        }

    def test_complete_valid_order(self):
        Order.objects.filter(id=3).update(
            **{"courier_id": 2, "assign_time": fake.date_time()}
        )
        url = reverse("api:order_complete")

        response = self.client.post(url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_complete_invalid_order(self):
        url = reverse("api:order_complete")

        response = self.client.post(url, self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
