from django import forms
from .models import PuzzleStatus, Puzzle, Answer


class NewPuzzleForm(forms.Form):
    name = forms.CharField(label="Puzzle Name", max_length=255)
    status = forms.ChoiceField(choices=PuzzleStatus.choices)
    rounds = forms.MultipleChoiceField(choices=[])
    url = forms.URLField(label="Puzzle URL", required=False)
    is_meta = forms.BooleanField(label="Meta?", required=False)

    def __init__(self, hunt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hunt = hunt
        
        self.fields["rounds"] = forms.MultipleChoiceField(choices=[
            (r.id, r.name) for r in hunt.round_set.all()
        ])

    # TODO: this sucks
    def make_puzzle(self):
        puzzle = Puzzle()
        puzzle.name = self.cleaned_data["name"]
        puzzle.hunt = self.hunt
        puzzle.status = self.cleaned_data["status"]
        puzzle.url = self.cleaned_data["url"]
        puzzle.is_meta = self.cleaned_data["is_meta"]
        puzzle.regenerate_puzzle_sheet()
        puzzle.save()
        for hunt_round in self.cleaned_data["rounds"]:
            print(hunt_round)
            puzzle.rounds.add(hunt_round)
        puzzle.save()
        return puzzle



class UpdatePuzzleForm(forms.Form):
    name = forms.CharField(label="Puzzle Name", max_length=255)
    rounds = forms.MultipleChoiceField(choices=[])
    status = forms.ChoiceField(choices=PuzzleStatus.choices)
    url = forms.URLField(label="Puzzle URL", required=False)
    is_meta = forms.BooleanField(label="Meta?", required=False)
    new_answer = forms.CharField(label="Add Answer", max_length=255, required=False)

    def __init__(self, puzzle, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        hunt = puzzle.hunt

        self.fields["name"].initial = puzzle.name

        self.fields["rounds"] = forms.MultipleChoiceField(choices=[
            (r.id, r.name) for r in hunt.round_set.all()
        ])

        self.fields["rounds"].initial = [r.id for r in puzzle.rounds.all()]

        self.fields["status"].initial = puzzle.status
        self.fields["url"].initial = puzzle.url
        self.fields["is_meta"].initial = puzzle.is_meta

    def update_puzzle(self, puzzle):
        puzzle.name = self.cleaned_data["name"]

        puzzle.rounds.clear()
        for hunt_round in self.cleaned_data["rounds"]:
            puzzle.rounds.add(hunt_round)

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