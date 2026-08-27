from .models import HuntMember
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

def user_can_see_hunt(view_func):
    def inner(req, hunt_id):
        if not req.user.is_authenticated:
            return HttpResponseRedirect(reverse("puzzles:login"))
        elif HuntMember.objects.filter(hunt__id=hunt_id, user=req.user).exists():
            return view_func(req, hunt_id)
        else:
            return HttpResponseRedirect("/")
    return inner

def user_can_see_puzzle(view_func):
    def inner(req, puzzle_id):
        if not req.user.is_authenticated:
            return HttpResponseRedirect(reverse("puzzles:login"))
        elif HuntMember.objects.filter(hunt=get_object_or_404(Puzzle, id=puzzle_id).hunt, user=req.user).exists():
            return view_func(req, hunt_id)
        else:
            return HttpResponseRedirect("/")
    return inner