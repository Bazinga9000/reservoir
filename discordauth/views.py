from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.urls import reverse
from dotenv import load_dotenv
from urllib.parse import quote
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")

from uuid import uuid4

def login(request):
    state = uuid4().hex
    request.session["state"] = state
    return HttpResponse(f"<a href=https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={quote(REDIRECT_URI)}&scope=identify&state={state}>discord sign in</a>")

def auth(request):
    if "code" not in request.GET \
        or request.session.get("state") is None \
        or len(request.session.get("state")) != 32 \
        or request.session.get("state") != request.GET.get("state"):
        raise PermissionDenied
    del request.session["state"] # no reuse
    user = authenticate(request, code=request.GET.get("code"))
    if user is not None:
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect(reverse("discordauth:login"))