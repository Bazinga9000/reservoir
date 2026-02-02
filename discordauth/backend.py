import requests
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.contrib.auth.backends import BaseBackend
from .local_settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from .models import DiscordUser
    
class DiscordAuthBackend(BaseBackend):
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, code=None):
        print("hell torment", code)
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        if code is None:
            return None
        else:
            req = requests.post(f"https://discord.com/api/oauth2/token", data=data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
            if req.status_code >= 300:
                return None
            resp = req.json()
            if resp.get("scope") != "identify" or resp.get("token_type") != "Bearer":
                return None
            token = resp.get("access_token")
            if token is None:
                return None
            headers = {
                "Authorization": f"Bearer {token}"
            }
            req = requests.get(f"https://discord.com/api/users/@me", headers=headers)
            if req.status_code >= 300:
                return None
            resp = req.json()
            uid = resp["id"]
            username = resp["username"]

            user, found = User.objects.get_or_create(username=str(uid))
            user.set_unusable_password()
            user.save()
            discord_user, _ = DiscordUser.objects.get_or_create(user=user, defaults={"cached_username": username})
            return user
            