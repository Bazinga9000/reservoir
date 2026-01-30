from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.urls import reverse
from uuid import uuid4

def login(request):
    state = uuid4().hex
    request.session["state"] = state
    return HttpResponse(f"<a href=https://discord.com/oauth2/authorize?client_id=1466557779702714592&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fauth&scope=identify&state={state}>discord sign in</a>")

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