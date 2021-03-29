from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class CourierDetailTests(APITestCase):
    fixtures = [
        "api/fixtures/courier_type.json",
        "api/tests/fixtures/couriers.json",
        "api/tests/fixtures/couriers_detail.json",
    ]

    def setUp(self):
        self.first_url_edit = reverse("api:courier_edit", kwargs={"courier_id": 1})
        self.second_url_edit = reverse("api:courier_edit", kwargs={"courier_id": 2})
        self.third_url_edit = reverse("api:courier_edit", kwargs={"courier_id": 3})

    def test_response(self):
        response = self.client.get(self.first_url_edit, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_param_in_response(self):
        response = self.client.get(self.first_url_edit, format="json")
        content = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("rating", content)
        self.assertIn("earnings", content)

    def test_first_courier_rating(self):
        response = self.client.get(self.first_url_edit, format="json")
        content = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.get("rating"), 2.92)

    def test_first_courier_earnings(self):
        response = self.client.get(self.first_url_edit, format="json")
        content = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.get("earnings"), 7500)

    def test_second_courier_rating(self):
        response = self.client.get(self.second_url_edit, format="json")
        content = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.get("rating"), 1.25)

    def test_second_courier_earnings(self):
        response = self.client.get(self.second_url_edit, format="json")
        content = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.get("earnings"), 7500)

    def test_third_courier_rating(self):
        response = self.client.get(self.third_url_edit, format="json")
        content = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("rating", content)

    def test_third_courier_earnings(self):
        response = self.client.get(self.third_url_edit, format="json")
        content = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content.get("earnings"), 0)
