from django.urls import path

from . import views

app_name = "discordauth"
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("auth/", views.auth, name="auth"),
    path("userpage/", views.user_page, name="userpage"),
    path("userpage/update", views.update_discord_user, name="update_discord_user")
]