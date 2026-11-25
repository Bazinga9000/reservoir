from django import forms
from .models import PuzzleStatus, Puzzle, Answer, DiscordUser, Theme, Color, TagKind

class NewPuzzleForm(forms.Form):
    name = forms.CharField(label="Puzzle Name", max_length=255)
    description = forms.CharField(label="Description", max_length=1000, required=False)
    is_meta = forms.BooleanField(label="Meta?", required=False)
    status = forms.ChoiceField(choices=PuzzleStatus.choices)
    url = forms.URLField(label="Puzzle URL", required=False)
    tags = forms.MultipleChoiceField(choices=[])

    def __init__(self, hunt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hunt = hunt
        
        self.fields["tags"] = forms.MultipleChoiceField(choices=[
            (r.id, str(r)) for r in hunt.tag_set.all()
        ])

    # TODO: this sucks
    def make_puzzle(self):
        puzzle = Puzzle()
        puzzle.name = self.cleaned_data["name"]
        puzzle.hunt = self.hunt
        puzzle.status = self.cleaned_data["status"]
        puzzle.url = self.cleaned_data["url"]
        puzzle.is_meta = self.cleaned_data["is_meta"]
        puzzle.description = self.cleaned_data["description"]
        puzzle.regenerate_puzzle_sheet()
        puzzle.save()
        for tag in self.cleaned_data["tags"]:
            print(tag)
            puzzle.tags.add(tag)
        puzzle.save()
        return puzzle



class UpdatePuzzleForm(forms.Form):
    name = forms.CharField(label="Puzzle Name", max_length=255)
    description = forms.CharField(label="Description", max_length=1000, required=False)
    tags = forms.MultipleChoiceField(choices=[])
    status = forms.ChoiceField(choices=PuzzleStatus.choices)
    url = forms.URLField(label="Puzzle URL", required=False)
    is_meta = forms.BooleanField(label="Meta?", required=False)
    new_answer = forms.CharField(label="Add Answer", max_length=255, required=False)

    def __init__(self, puzzle, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        hunt = puzzle.hunt

        self.fields["name"].initial = puzzle.name
        self.fields["description"].initial = puzzle.description

        self.fields["tags"] = forms.MultipleChoiceField(choices=[
            (r.id, str(r)) for r in hunt.tag_set.all()
        ])

        self.fields["tags"].initial = [r.id for r in puzzle.tags.all()]

        self.fields["status"].initial = puzzle.status
        self.fields["url"].initial = puzzle.url
        self.fields["is_meta"].initial = puzzle.is_meta

    def update_puzzle(self, puzzle):
        old_name = puzzle.name
        puzzle.name = self.cleaned_data["name"]
        if old_name != puzzle.name:
            puzzle.rename_puzzle_sheet()

        puzzle.description = self.cleaned_data["description"]


        puzzle.tags.clear()
        for tag in self.cleaned_data["tags"]:
            puzzle.tags.add(tag)

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

class NewTagForm(forms.Form):
    kind = forms.ChoiceField(choices=TagKind.choices)
    name = forms.CharField(label="Tag Name", max_length=255)

    def __init__(self, hunt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hunt = hunt

    def create_tag(self):
        tag = Tag(kind=self.cleaned_data["kind"], 
                  name=self.cleaned_data["name"], 
                  hunt=self.hunt)
        tag.save()
        return tag

class UpdateDiscordUserForm(forms.Form):
    linked_gmail = forms.EmailField(label="Google Email", required=False)
    chosen_theme = forms.ChoiceField(choices=Theme.choices)
    chat_color = forms.ChoiceField(choices=Color.choices)

    def __init__(self, discord_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

        self.fields["linked_gmail"].initial = discord_user.linked_gmail
        self.fields["chosen_theme"].initial = discord_user.chosen_theme
        self.fields["chat_color"].initial = discord_user.chat_color

    def update_user(self, discord_user):
        discord_user.linked_gmail = self.cleaned_data["linked_gmail"]
        discord_user.chosen_theme = self.cleaned_data["chosen_theme"]
        discord_user.chat_color = self.cleaned_data["chat_color"]
        discord_user.save()