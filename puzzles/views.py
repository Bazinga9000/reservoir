from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, logout, login


from .models import Hunt, Round, Puzzle, PuzzleStatus, Answer
from .forms import NewPuzzleForm, UpdatePuzzleForm, UpdateDiscordUserForm
from os import getenv
from urllib.parse import quote

DISCORD_CLIENT_ID = getenv("DISCORD_CLIENT_ID")
DISCORD_REDIRECT_URI = getenv("DISCORD_REDIRECT_URI")

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
        return HttpResponseRedirect(reverse("puzzles:login"))

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

    return HttpResponseRedirect(reverse("puzzles:userpage"))


@login_required()
def bigboard(request, hunt_id):
    hunt = get_object_or_404(Hunt, pk=hunt_id)

    return render(request, "puzzles/bigboard.html", {
        "hunt": hunt,
        "new_puzzle_form": NewPuzzleForm(hunt)
    })

@login_required()
def puzzlepage(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, pk=puzzle_id)
    return render(request, "puzzles/puzzlepage.html", {
        "puzzle": puzzle,
        "update_puzzle_form": UpdatePuzzleForm(puzzle)
    })

def update(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, pk=puzzle_id)
    
    if request.method == "POST":
        form = UpdatePuzzleForm(puzzle, request.POST)
        if form.is_valid():
            form.update_puzzle(puzzle)

        # todo: there is definitely a better way to handle answer deletion 
        for answer in puzzle.answer_set.all():
            if request.POST.get(f"delete_answer_{answer.id}", False):
                answer.delete()

    return HttpResponseRedirect(reverse("puzzles:puzzlepage", args=(puzzle.id,)))


def new_round(request, hunt_id):
    hunt = get_object_or_404(Hunt, pk=hunt_id)

    new_round_name = request.POST["new_round"]
    if new_round_name != "" and len(new_round_name) < 255:
        rnd = Round()
        rnd.name = new_round_name
        rnd.hunt = hunt
        rnd.save()

    return HttpResponseRedirect(reverse("puzzles:bigboard", args=(hunt.id,)))


def new_puzzle(request, hunt_id):
    hunt = get_object_or_404(Hunt, pk=hunt_id)
    hunt_round = get_object_or_404(Round, pk=1)

    if hunt_round.hunt.id != hunt.id:
        raise Http404("This round is for a different hunt than the given hunt")

    if request.method == "POST":
        form = NewPuzzleForm(hunt, request.POST)
        if form.is_valid():
            puzzle = form.make_puzzle()
            puzzle.save()
    
    return HttpResponseRedirect(reverse("puzzles:bigboard", args=(hunt.id,)))

def landing(request):
    return render(request, "puzzles/landing.html", {
        "hunts": Hunt.objects.all(),
        "team_name": getenv("TEAM_NAME")
    })