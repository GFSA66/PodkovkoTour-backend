from django.urls import path

from .views import BookingRequestCreateView, TourDetailView, TourListView

urlpatterns = [
    path("tours/", TourListView.as_view(), name="tour-list"),
    path("tours/<int:pk>/", TourDetailView.as_view(), name="tour-detail"),
    path("booking-requests/", BookingRequestCreateView.as_view(), name="booking-request-create"),
]