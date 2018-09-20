from django.urls import path
from .views import (
    SearchReservationPageView, ReservationPageView, ReservationListView,
    ReservationDetailView, ReservationDeleteView, GeneratePDF) 


urlpatterns = [
    # Path of reservation
    path('', SearchReservationPageView.as_view(), name="reservations_search"),
    path('reserve/<int:id>/', ReservationPageView.as_view(), name="reservation_reserve"),
    path('list/', ReservationListView.as_view(), name="reservation_list"),
    path('<uuid:pk>/<slug:slug>/', ReservationDetailView.as_view(), name='reservation_detail'),
    path('<uuid:pk>/', ReservationDeleteView.as_view(), name='reservation_delete'),
    path('reserve/pdf/<uuid:id>', GeneratePDF.as_view(), name='reservation_get_pdf'),
]