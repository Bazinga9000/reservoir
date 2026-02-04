from django.db import models
from django.core.exceptions import ValidationError
from . import google

class PuzzleStatus(models.TextChoices):
    LOCKED = 'LO', "Locked"
    NOT_STARTED = 'NS', "Not Started"
    IN_PROGRESS = 'IP', "In Progress"
    STUCK = 'ST', "Stuck"
    NES = 'EX', "Now Extract Somehow" 
    SOLVED = 'SL', "Solved"

class Hunt(models.Model):
    name = models.CharField(max_length=255)

    team_user = models.CharField(max_length=64)
    team_pw = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"
    
    def count_puzzles_of_status(self, status: PuzzleStatus):
        return self.puzzle_set.filter(status__exact=status).count()
    
    def total_puzzles(self):
        return self.puzzle_set.count()
    
    def num_locked(self):
        return self.count_puzzles_of_status(PuzzleStatus.LOCKED)

    def num_solved(self):
        return self.count_puzzles_of_status(PuzzleStatus.SOLVED)
    
    def num_available(self):
        return self.total_puzzles() - self.num_solved() - self.num_locked()
    
    def meta_solves(self):
        return self.puzzle_set.filter(status__exact=PuzzleStatus.SOLVED, is_meta__exact=True).count()

    def roundless_puzzles(self):
        return self.puzzle_set.filter(rounds=None).all()

class Round(models.Model):
    name = models.CharField(max_length=255)
    hunt = models.ForeignKey(Hunt, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    def puzzles_ordered(self):
        # TODO: human sort the name? We might have something weird like shell game with numbered puzzles that goes over 10?
        return self.puzzle_set.order_by("-is_meta", "name").all()

class Puzzle(models.Model):
    name = models.CharField(max_length=255)
    hunt = models.ForeignKey(Hunt, on_delete=models.CASCADE)
    rounds = models.ManyToManyField(Round, through="PuzzleRoundField")
    url = models.URLField()
    is_meta = models.BooleanField(default=False)
    sheet_id = models.CharField(max_length=255, default="")

    status = models.CharField(max_length=2, choices=PuzzleStatus.choices, default=PuzzleStatus.LOCKED)

    def __str__(self):
        return f"{self.name}"
    
    def regenerate_puzzle_sheet(self):
        # This won't delete the old sheet, but it will make the site show you the new one.
        self.sheet_id = google.make_puzzle_sheet(f"{self.name}")
        self.save()

    def rename_puzzle_sheet(self):
        google.rename_sheet(self.sheet_id, self.name)

    def sheet_url(self):
        # Make a sheet if one does not exist
        if self.sheet_id == "":
            self.regenerate_puzzle_sheet()
        
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit"


class PuzzleRoundField(models.Model):
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    hunt_round  = models.ForeignKey(Round, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["puzzle", "hunt_round"], name="no_duplicate_links"),
        ]

    def clean(self):
        if self.puzzle.hunt.id != self.hunt_round.hunt.id:
                raise ValidationError(f"Round {self.hunt_round.name} is not in hunt {self.puzzle.hunt.name}")

class Answer(models.Model):
    answer_text = models.CharField(max_length=255)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.answer_text}"