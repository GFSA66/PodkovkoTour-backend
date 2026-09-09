from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BookingRequestCreateView,
    BookingRequestHistoryView,
    CountryViewSet,
    DepartureCityViewSet,
    GoalCityViewSet,
    PinnedReviewsView,
    TourOperatorViewSet,
    TourReviewListCreateView,
    TourViewSet,
    meal_types,
    resorts,
)

router = DefaultRouter()
router.register("countries", CountryViewSet)
router.register("departure-cities", DepartureCityViewSet)
router.register("goal-cities", GoalCityViewSet)
router.register("tour-operators", TourOperatorViewSet)
router.register("tours", TourViewSet)

urlpatterns = [
    path("booking-requests/", BookingRequestCreateView.as_view(), name="booking-request-create"),
    path("meal-types/", meal_types, name="meal-types"),
    path("resorts/", resorts, name="resorts"),
    path("", include(router.urls)),
    path("tours/<int:tour_id>/reviews/", TourReviewListCreateView.as_view(), name="tour-reviews"),
    path("reviews/pinned/", PinnedReviewsView.as_view(), name="pinned-reviews"),
    path("booking-requests/mine/", BookingRequestHistoryView.as_view(), name="booking-request-history"),
]