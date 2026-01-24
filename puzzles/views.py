from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Hunt, PuzzleStatus

def bigboard(request, hunt_id):
    hunt = get_object_or_404(Hunt, pk=hunt_id)

    total_puzzles = hunt.total_puzzles()

    num_solved = hunt.count_puzzles_of_status(PuzzleStatus.SOLVED)
    num_locked = hunt.count_puzzles_of_status(PuzzleStatus.LOCKED)

    
    out = f"""
    <h1>{hunt.name}</h1>
    Total Puzzles: <b>{total_puzzles}</b>
    Locked Puzzles: <b>{num_locked}</b>
    Solved Puzzles: <b>{num_solved}</b>
    Avaliable Puzzles: <b>{total_puzzles - num_locked - num_solved}</b>
    """

    return HttpResponse(out)