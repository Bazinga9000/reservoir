from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from dotenv import load_dotenv
from urllib.parse import quote
import os

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import DiscordUser
from .forms import UpdateDiscordUserForm

load_dotenv()

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")

from uuid import uuid4

def login_view(request):
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
        login(request, user)
        # if request.session["next"] is not None:
        #     return HttpResponseRedirect(request.session["next"])
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect(reverse("discordauth:login"))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

@login_required()
def user_page(request):
    du = request.user.discorduser

    return render(request, "puzzles/userpage.html", {
        "update_user_form": UpdateDiscordUserForm(du)
    })

@login_required()
def update_discord_user(request):
    du = request.user.discorduser
    
    if request.method == "POST":
        form = UpdateDiscordUserForm(du, request.POST)
        if form.is_valid():
            form.update_user(du)


    return HttpResponseRedirect(reverse("discordauth:userpage"))