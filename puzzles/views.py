from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Hunt, Puzzle

def bigboard(request, hunt_id):
    hunt = get_object_or_404(Hunt, pk=hunt_id)

    return render(request, "puzzles/bigboard.html", {"hunt": hunt})

def puzzlepage(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, pk=puzzle_id)

    return render(request, "puzzles/puzzlepage.html", {"puzzle": puzzle})
