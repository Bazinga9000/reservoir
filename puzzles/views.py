from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import Hunt, Round, Puzzle, PuzzleStatus, Answer

def bigboard(request, hunt_id):
    hunt = get_object_or_404(Hunt, pk=hunt_id)

    return render(request, "puzzles/bigboard.html", {"hunt": hunt})

def puzzlepage(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, pk=puzzle_id)

    return render(request, "puzzles/puzzlepage.html", {
        "puzzle": puzzle,
        "puzzle_statuses": PuzzleStatus
    })

def update(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, pk=puzzle_id)
    
    # TODO: proper validation

    # Update puzzle status
    new_status = request.POST["status"]
    puzzle.status = new_status
    puzzle.save()

    # Delete any requested answer
    for answer in puzzle.answer_set.all():
        if request.POST.get(f"delete_answer_{answer.id}", False):
            answer.delete()

    # Add new answer
    new_answer_text = request.POST["new_answer"]
    if new_answer_text != "" and len(new_answer_text) < 255:
        ans = Answer()
        ans.answer_text = new_answer_text.upper()
        ans.puzzle = puzzle
        ans.save() 

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