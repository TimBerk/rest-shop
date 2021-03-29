from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.order import Order, OrderDelivery
from api.models.courier import Courier, CourierWork, CourierRegion


class CourierEditTests(APITestCase):
    fixtures = [
        "api/fixtures/courier_type.json",
        "api/tests/fixtures/couriers.json",
        "api/tests/fixtures/couriers_edit.json",
    ]

    def setUp(self):
        self.first_url_edit = reverse("api:courier_edit", kwargs={"courier_id": 1})

    def test_valid_response(self):
        data = {"regions": [1, 12, 22, 23]}
        response = self.client.patch(self.first_url_edit, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_response(self):
        data = {"week": 1}
        response = self.client.patch(self.first_url_edit, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CourierEditRegionTests(APITestCase):
    fixtures = [
        "api/fixtures/courier_type.json",
        "api/tests/fixtures/couriers.json",
        "api/tests/fixtures/couriers_edit.json",
    ]

    def setUp(self):
        self.first_url_edit = reverse("api:courier_edit", kwargs={"courier_id": 1})
        self.remove_data = {"regions": [1, 22]}
        self.empty_data = {"regions": []}
        self.str_data = {"regions": ["test"]}

    def test_add_region(self):
        data = {"regions": [1, 12, 22, 23]}
        response = self.client.patch(self.first_url_edit, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CourierRegion.objects.filter(courier_id=1).count(), 4)

    def test_remove_region(self):
        response = self.client.patch(
            self.first_url_edit, data=self.remove_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CourierRegion.objects.filter(courier_id=1).count(), 2)

    def test_remove_region_orders(self):
        response = self.client.patch(
            self.first_url_edit, data=self.remove_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Order.objects.filter(courier_id=1, region=12, is_delivered=False).count(), 0
        )

    def test_empty_region(self):
        response = self.client.patch(
            self.first_url_edit, data=self.empty_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CourierRegion.objects.filter(courier_id=1).count(), 0)

    def test_empty_region_orders(self):
        response = self.client.patch(
            self.first_url_edit, data=self.empty_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Order.objects.filter(courier_id=1, is_delivered=False).count(), 0
        )

    def test_add_str_region(self):
        response = self.client.patch(
            self.first_url_edit, data=self.str_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CourierEditTypeTests(APITestCase):
    fixtures = [
        "api/fixtures/courier_type.json",
        "api/tests/fixtures/couriers.json",
        "api/tests/fixtures/couriers_edit.json",
    ]

    def setUp(self):
        self.courier_id = 1
        self.assign_time = "2021-01-10T09:32:14.42Z"
        self.first_url_edit = reverse(
            "api:courier_edit", kwargs={"courier_id": self.courier_id}
        )
        self.bike_type = {"courier_type": "bike"}
        self.car_type = {"courier_type": "car"}
        self.foot_type = {"courier_type": "foot"}
        self.empty_data = {"courier_type": ""}

    def test_response(self):
        response = self.client.patch(
            self.first_url_edit, data=self.bike_type, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json().get("courier_type"), self.bike_type.get("courier_type")
        )

    def test_foot_to_bike_type(self):
        response = self.client.patch(
            self.first_url_edit, data=self.bike_type, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_foot_to_car_type(self):
        response = self.client.patch(
            self.first_url_edit, data=self.car_type, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bike_to_foot_type(self):
        Courier.objects.filter(id=self.courier_id).update(type="bike")
        Order.objects.filter(id=3).update(
            courier_id=self.courier_id, assign_time=self.assign_time
        )

        response = self.client.patch(
            self.first_url_edit, data=self.foot_type, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bike_to_foot_type_orders(self):
        Courier.objects.filter(id=self.courier_id).update(type="bike")
        Order.objects.filter(id=3).update(
            courier_id=self.courier_id, assign_time=self.assign_time
        )

        self.client.patch(self.first_url_edit, data=self.foot_type, format="json")
        self.assertEqual(
            Order.objects.filter(
                courier_id=self.courier_id, is_delivered=False
            ).count(),
            2,
        )

    def test_empty_type(self):
        response = self.client.patch(
            self.first_url_edit, data=self.empty_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CourierEditWorkingHoursTests(APITestCase):
    fixtures = [
        "api/fixtures/courier_type.json",
        "api/tests/fixtures/couriers.json",
        "api/tests/fixtures/couriers_edit.json",
    ]

    def setUp(self):
        self.courier_id = 1
        self.assign_time = "2021-01-10T09:32:14.42Z"
        self.first_url_edit = reverse(
            "api:courier_edit", kwargs={"courier_id": self.courier_id}
        )
        self.add_data = {"working_hours": ["11:35-14:05", "09:00-11:00", "16:00-20:00"]}
        self.empty_data = {"working_hours": []}
        self.change_data = {"working_hours": ["09:00-11:00", "16:00-20:00"]}

    def test_add_hours(self):
        response = self.client.patch(
            self.first_url_edit, data=self.add_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_hours_response(self):
        response = self.client.patch(
            self.first_url_edit, data=self.add_data, format="json"
        )
        self.assertEqual(
            response.json().get("working_hours"), self.add_data.get("working_hours")
        )

    def test_add_hours_db(self):
        self.client.patch(self.first_url_edit, data=self.add_data, format="json")
        self.assertEqual(
            CourierWork.objects.filter(courier_id=self.courier_id).count(), 3
        )

    def test_empty_hours(self):
        response = self.client.patch(
            self.first_url_edit, data=self.empty_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_hours_response(self):
        response = self.client.patch(
            self.first_url_edit, data=self.empty_data, format="json"
        )
        self.assertEqual(
            response.json().get("working_hours"), self.empty_data.get("working_hours")
        )

    def test_empty_hours_db(self):
        self.client.patch(self.first_url_edit, data=self.empty_data, format="json")
        self.assertEqual(
            CourierWork.objects.filter(courier_id=self.courier_id).count(), 0
        )

    def test_empty_hours_orders_db(self):
        self.client.patch(self.first_url_edit, data=self.empty_data, format="json")
        self.assertEqual(
            Order.objects.filter(
                courier_id=self.courier_id, is_delivered=False
            ).count(),
            0,
        )

    def test_change_hours(self):
        response = self.client.patch(
            self.first_url_edit, data=self.change_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_hours_order_db(self):
        response = self.client.patch(
            self.first_url_edit, data=self.change_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Order.objects.filter(
                courier_id=self.courier_id, is_delivered=False
            ).count(),
            1,
        )

    def test_change_hours_order_2_db(self):
        OrderDelivery.objects.filter(id=5).update(**{"time_to": "16:30"})
        response = self.client.patch(
            self.first_url_edit, data=self.change_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Order.objects.filter(
                courier_id=self.courier_id, is_delivered=False
            ).count(),
            2,
        )
