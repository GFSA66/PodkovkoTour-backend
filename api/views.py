from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from Tour.models import Country, DepartureCity, GoalCity, TourOperator, Tour, BookingRequest, Hotel
from .serializers import (
    CountrySerializer, DepartureCitySerializer, GoalCitySerializer, TourOperatorSerializer,
    TourListSerializer, TourDetailSerializer, BookingRequestSerializer,
)


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.order_by("name")
    serializer_class = CountrySerializer
    pagination_class = None


class DepartureCityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DepartureCity.objects.order_by("name")
    serializer_class = DepartureCitySerializer
    pagination_class = None


class GoalCityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GoalCity.objects.order_by("name")
    serializer_class = GoalCitySerializer
    pagination_class = None


class TourOperatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TourOperator.objects.order_by("name")
    serializer_class = TourOperatorSerializer
    pagination_class = None


@api_view(["GET"])
def meal_types(request):
    """GET /api/meal-types/ -> [{"value": "AI", "label": "Все включено"}, ...]"""
    return Response([{"value": v, "label": l} for v, l in Tour.MealType.choices])


@api_view(["GET"])
def resorts(request):
    """GET /api/resorts/ -> уникальные курортные зоны отелей (Hotel.resort)"""
    names = (
        Hotel.objects.exclude(resort="")
        .values_list("resort", flat=True)
        .distinct()
        .order_by("resort")
    )
    return Response([{"id": n, "name": n} for n in names])


class TourViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Tour.objects.filter(status=Tour.Status.ACTIVE)
        .select_related("hotel", "hotel__country", "departure_city", "goal_city", "tour_operator")
        .prefetch_related("hotel__photos")
    )
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_hot", "departure_city", "goal_city", "tour_operator", "meal_type", "hotel__country"]
    pagination_class = None  # фронт сейчас грузит весь список и фильтрует на клиенте

    def get_serializer_class(self):
        return TourDetailSerializer if self.action == "retrieve" else TourListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class BookingRequestViewSet(viewsets.ModelViewSet):
    queryset = BookingRequest.objects.all()
    serializer_class = BookingRequestSerializer
    http_method_names = ["post", "head", "options"]