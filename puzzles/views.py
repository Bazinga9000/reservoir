from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse

from .models import Hunt, Round, Puzzle, PuzzleStatus, Answer
from .forms import NewPuzzleForm, UpdatePuzzleForm

def bigboard(request, hunt_id):
    hunt = get_object_or_404(Hunt, pk=hunt_id)

    return render(request, "puzzles/bigboard.html", {
        "hunt": hunt,
        "new_puzzle_form": NewPuzzleForm()
    })

def puzzlepage(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, pk=puzzle_id)
    return render(request, "puzzles/puzzlepage.html", {
        "puzzle": puzzle,
        "update_puzzle_form": UpdatePuzzleForm(initial={
            "name": puzzle.name,
            "status": puzzle.status,
            "url": puzzle.url,
            "is_meta": puzzle.is_meta
        })
    })

def update(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, pk=puzzle_id)
    
    if request.method == "POST":
        form = UpdatePuzzleForm(request.POST)
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


def new_puzzle(request, hunt_id, round_id):
    hunt = get_object_or_404(Hunt, pk=hunt_id)
    hunt_round = get_object_or_404(Round, pk=round_id)

    if hunt_round.hunt.id != hunt.id:
        raise Http404("This round is for a different hunt than the given hunt")

    if request.method == "POST":
        form = NewPuzzleForm(request.POST)
        if form.is_valid():
            puzzle = form.make_puzzle()
            puzzle.hunt_round = hunt_round
            puzzle.save()
    
    return HttpResponseRedirect(reverse("puzzles:bigboard", args=(hunt.id,)))