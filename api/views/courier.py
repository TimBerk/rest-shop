from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models.courier import Courier
from api.schemas.courier import (
    CouriersPostRequest,
    COURIERS_RESPONSE,
    CourierUpdateRequest,
    COURIER_PATCH_RESPONSE,
    COURIER_GET_RESPONSE,
)
from api.serializers.courier import (
    CourierSerializer,
    CourierUpdateSerializer,
    CourierRetrieveSerializer,
)


class CouriersView(APIView):
    @swagger_auto_schema(
        request_body=CouriersPostRequest(),
        responses=COURIERS_RESPONSE,
        operation_summary="Import couriers",
        tags=["Couriers"],
    )
    def post(self, request, format=None):
        data = request.data
        errors = []
        success = []

        for courier in data:
            try:
                serializer = CourierSerializer(data=courier)
                if serializer.is_valid():
                    serializer.save()
                    success.append({"id": courier.get("courier_id")})

                else:
                    errors.append({"id": courier.get("courier_id")})
            except Exception as exc:
                errors.append({"id": courier.get("courier_id")})

        if errors:
            return Response(
                {"validation_error": {"couriers": errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"couriers": success}, status=status.HTTP_201_CREATED)


class CourierView(APIView):
    @swagger_auto_schema(
        request_body=CourierUpdateRequest(),
        responses=COURIER_PATCH_RESPONSE,
        operation_summary="Update courier by id",
        tags=["Couriers"],
    )
    def patch(self, request, courier_id, format=None):
        courier = Courier.objects.filter(id=courier_id).first()
        if courier is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer = CourierUpdateSerializer(courier, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses=COURIER_GET_RESPONSE,
        operation_summary="Get courier by id",
        tags=["Couriers"],
    )
    def get(self, request, courier_id, format=None):
        courier = Courier.objects.filter(id=courier_id).first()
        if courier is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = CourierRetrieveSerializer(courier)
        return Response(serializer.data, status=status.HTTP_200_OK)
