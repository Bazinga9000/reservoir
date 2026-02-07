from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, logout
from django.urls import reverse
from dotenv import load_dotenv
from urllib.parse import quote
import os

load_dotenv()

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")

from uuid import uuid4

def login(request):
    state = uuid4().hex
    request.session["state"] = state
    # request.session["next"] = request.GET.get("next")
    return HttpResponseRedirect(f"https://discord.com/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&response_type=code&redirect_uri={quote(DISCORD_REDIRECT_URI)}&scope=identify&state={state}")

def auth(request):
    if "code" not in request.GET \
        or request.session.get("state") is None \
        or len(request.session.get("state")) != 32 \
        or request.session.get("state") != request.GET.get("state"):
        raise PermissionDenied
    del request.session["state"] # no reuse
    user = authenticate(request, code=request.GET.get("code"))
    if user is not None:
        # if request.session["next"] is not None:
        #     return HttpResponseRedirect(request.session["next"])
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect(reverse("discordauth:login"))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")