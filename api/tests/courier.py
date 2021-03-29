from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models.courier import Courier


class CouriersTests(APITestCase):
    fixtures = ["api/fixtures/courier_type.json"]

    def setUp(self):
        self.valid_payload = [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"],
            },
            {
                "courier_id": 2,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"],
            },
            {
                "courier_id": 3,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": [],
            },
        ]
        self.invalid_payload = [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "week": 1,
                "working_hours": ["11:35-14:05", "09:00-11:00"],
            },
            {
                "courier_id": 2,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"],
            },
            {"courier_id": 3, "courier_type": "car", "working_hours": []},
        ]

    def test_valid_response(self):
        url = reverse("api:couriers")
        response = self.client.post(url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_valid_couriers_response(self):
        url = reverse("api:couriers")
        valid_couriers = [{"id": 1}, {"id": 2}, {"id": 3}]
        response = self.client.post(url, self.valid_payload, format="json")
        content = response.json()
        self.assertEqual(content.get("couriers"), valid_couriers)

    def test_valid_couriers_db(self):
        url = reverse("api:couriers")
        self.client.post(url, self.valid_payload, format="json")
        self.assertEqual(Courier.objects.count(), 3)

    def test_invalid_response(self):
        url = reverse("api:couriers")
        response = self.client.post(url, self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_couriers_response(self):
        url = reverse("api:couriers")
        invalid_couriers = [{"id": 1}, {"id": 3}]
        response = self.client.post(url, self.invalid_payload, format="json")
        content = response.json()
        self.assertEqual(
            content.get("validation_error").get("couriers"), invalid_couriers
        )

    def test_invalid_couriers_db(self):
        url = reverse("api:couriers")
        self.client.post(url, self.invalid_payload, format="json")
        self.assertEqual(Courier.objects.count(), 1)
