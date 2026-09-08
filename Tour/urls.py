from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BookingRequestCreateView,
    CountryViewSet,
    DepartureCityViewSet,
    GoalCityViewSet,
    TourOperatorViewSet,
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
]