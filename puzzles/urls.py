from django.urls import path

from . import views

app_name = "puzzles"
urlpatterns = [
    # path("", views.index, name="index"),
    path("hunt/<int:hunt_id>/", views.bigboard, name="bigboard"),
    path("puzzle/<int:puzzle_id>/", views.puzzlepage, name="puzzlepage"),
    path("puzzle/<int:puzzle_id>/update", views.update, name="update")
]