
from django.urls import path
from . import views

urlpatterns = [
    path("", views.food_list, name="food_list"),
    path("add/", views.add_food, name="add_food"),
    path("my/", views.my_donations, name="my_donations"),
    path("requests/", views.request_list, name="request_list"),
    path("requests/<int:pk>/approve/", views.approve_request, name="approve_request"),
    path("requests/<int:pk>/reject/", views.reject_request, name="reject_request"),
    path("<int:pk>/", views.food_detail, name="food_detail"),
    path("<int:pk>/request/", views.request_food, name="request_food"),
]
