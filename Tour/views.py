from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .notifications import send_booking_notification
from .models import BookingRequest, Country, DepartureCity, GoalCity, Hotel, Tour, TourOperator, Review
from rest_framework import generics
from api.serializers import (
    BookingRequestCreateSerializer,
    CountrySerializer,
    DepartureCitySerializer,
    GoalCitySerializer,
    TourDetailSerializer,
    TourListSerializer,
    TourOperatorSerializer,
    BookingRequestHistorySerializer,
)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import ReviewCreateSerializer, ReviewSerializer


class TourReviewListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tours/<tour_id>/reviews/  — опубліковані відгуки, усім.
    POST /api/tours/<tour_id>/reviews/  — новий відгук, лише залогіненим.
    """

    def get_queryset(self):
        return Review.objects.filter(
            tour_id=self.kwargs["tour_id"], is_published=True
        ).order_by("-created_at")

    def get_serializer_class(self):
        return ReviewCreateSerializer if self.request.method == "POST" else ReviewSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["tour_id"] = self.kwargs["tour_id"]
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Дякуємо! Ваш відгук зʼявиться після модерації."},
            status=status.HTTP_201_CREATED,
        )

class PinnedReviewsView(generics.ListAPIView):
    """GET /api/reviews/pinned/ — до 3 закріплених і опублікованих відгуків
    для блоку "Про турагента" на головній."""

    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Review.objects.filter(is_published=True, is_pinned=True).order_by("-created_at")[:3]

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
    """GET /api/resorts/ -> унікальні курортні зони готелів (Hotel.resort)."""
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
    pagination_class = None  # фронт зараз вантажить весь список і фільтрує на клієнті

    def get_serializer_class(self):
        return TourDetailSerializer if self.action == "retrieve" else TourListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class BookingRequestCreateView(generics.CreateAPIView):
    serializer_class = BookingRequestCreateSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        send_booking_notification(booking)

class BookingRequestCreateView(generics.CreateAPIView):
    serializer_class = BookingRequestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        send_booking_notification(booking)


class BookingRequestHistoryView(generics.ListAPIView):
    serializer_class = BookingRequestHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            BookingRequest.objects.filter(user=self.request.user)
            .select_related("tour__hotel__country")
            .prefetch_related("tour__hotel__photos")
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx