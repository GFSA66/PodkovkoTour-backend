from rest_framework import generics

from Tour.models import Tour
from .serializers import (
    BookingRequestCreateSerializer,
    TourDetailSerializer,
    TourListSerializer,
)


class TourListView(generics.ListAPIView):
    """GET /api/tours/         — все активные туры
    GET /api/tours/?hot=true  — только горящие (для главной)
    """

    serializer_class = TourListSerializer

    def get_queryset(self):
        qs = (
            Tour.objects.filter(status=Tour.Status.ACTIVE)
            .select_related("hotel__country")
            .prefetch_related("hotel__photos")
            .order_by("-is_hot", "departure_date")
        )
        if self.request.query_params.get("hot") == "true":
            qs = qs.filter(is_hot=True)
        return qs


class TourDetailView(generics.RetrieveAPIView):
    """GET /api/tours/<id>/ — полная карточка тура с галереей и описанием."""

    queryset = Tour.objects.select_related("hotel__country").prefetch_related("hotel__photos")
    serializer_class = TourDetailSerializer


class BookingRequestCreateView(generics.CreateAPIView):
    """POST /api/booking-requests/ — заявка из формы на сайте."""

    serializer_class = BookingRequestCreateSerializer