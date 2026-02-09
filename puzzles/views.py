from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Hunt, Round, Puzzle, PuzzleStatus, Answer
from .forms import NewPuzzleForm, UpdatePuzzleForm
from os import getenv

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