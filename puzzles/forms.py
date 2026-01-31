from django import forms
from .models import PuzzleStatus, Puzzle, Answer


class NewPuzzleForm(forms.Form):
    name = forms.CharField(label="Puzzle Name", max_length=255)
    status = forms.ChoiceField(choices=PuzzleStatus.choices)
    url = forms.URLField(label="Puzzle URL", required=False)
    is_meta = forms.BooleanField(label="Meta?", required=False)

    def make_puzzle(self):
        puzzle = Puzzle()
        puzzle.name = self.cleaned_data["name"]
        puzzle.status = self.cleaned_data["status"]
        puzzle.url = self.cleaned_data["url"]
        puzzle.is_meta = self.cleaned_data["is_meta"]
        return puzzle



class UpdatePuzzleForm(forms.Form):
    name = forms.CharField(label="Puzzle Name", max_length=255)
    status = forms.ChoiceField(choices=PuzzleStatus.choices)
    url = forms.URLField(label="Puzzle URL", required=False)
    is_meta = forms.BooleanField(label="Meta?", required=False)
    new_answer = forms.CharField(label="Add Answer", max_length=255, required=False)

    def update_puzzle(self, puzzle):
        puzzle.name = self.cleaned_data["name"]
        puzzle.status = self.cleaned_data["status"]
        puzzle.url = self.cleaned_data["url"]
        puzzle.is_meta = self.cleaned_data["is_meta"]
        puzzle.save()

        na = self.cleaned_data["new_answer"]
        if na != "":
            ans = Answer()
            ans.answer_text = na.upper()
            ans.puzzle = puzzle
            ans.save()