
from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>/", views.track_donation, name="track_donation"),
    path(
        "<int:pk>/update/",
        views.update_tracking,
        name="update_tracking",
    ),
]
