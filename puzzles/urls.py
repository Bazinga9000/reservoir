from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    # path("", views.index, name="index"),
    path("<int:hunt_id>/", views.bigboard, name="bigboard"),
]