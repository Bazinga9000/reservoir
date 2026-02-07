from django.urls import path

from . import views

app_name = "discordauth"
urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("auth/", views.auth, name="auth"),
]