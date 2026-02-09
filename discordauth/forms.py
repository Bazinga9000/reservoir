from django import forms
from .models import DiscordUser, Theme



class UpdateDiscordUserForm(forms.Form):
    linked_gmail = forms.URLField(label="Google Email", required=False)
    chosen_theme = forms.ChoiceField(choices=Theme.choices)

    def __init__(self, discord_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

        self.fields["linked_gmail"].initial = discord_user.linked_gmail
        self.fields["chosen_theme"].initial = discord_user.chosen_theme

    def update_user(self, discord_user):
        discord_user.linked_gmail = self.cleaned_data["linked_gmail"]
        discord_user.chosen_theme = self.cleaned_data["chosen_theme"]
        discord_user.save()