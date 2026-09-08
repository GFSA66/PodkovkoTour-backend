from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("countries", views.CountryViewSet, basename="country")
router.register("departure-cities", views.DepartureCityViewSet, basename="departure-city")
router.register("goal-cities", views.GoalCityViewSet, basename="goal-city")
router.register("tour-operators", views.TourOperatorViewSet, basename="tour-operator")
router.register("tours", views.TourViewSet, basename="tour")
router.register("booking-requests", views.BookingRequestViewSet, basename="booking-request")

urlpatterns = [
    path("meal-types/", views.meal_types, name="meal-types"),
    path("resorts/", views.resorts, name="resorts"),
    path("", include(router.urls)),
]