from django.urls import path

from . import views

app_name = "puzzles"
urlpatterns = [
    path("", views.landing, name="landing"),
    path("hunt/<int:hunt_id>/", views.bigboard, name="bigboard"),
    path("puzzle/<int:puzzle_id>/", views.puzzlepage, name="puzzlepage"),
    path("puzzle/<int:puzzle_id>/update", views.update, name="update"),
    path("hunt/<int:hunt_id>/new_round", views.new_round, name="new_round"),
    path("hunt/<int:hunt_id>/new_puzzle", views.new_puzzle, name="new_puzzle"),

    
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("auth/", views.auth, name="auth"),
    path("userpage/", views.user_page, name="userpage"),
    path("userpage/update", views.update_discord_user, name="update_discord_user")
]