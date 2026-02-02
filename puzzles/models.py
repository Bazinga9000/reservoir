from django.db import models
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
        count = 0
        for round in self.round_set.all():
            count += round.puzzle_set.filter(status__exact=status).count()
        
        return count
    
    def total_puzzles(self):
        count = 0
        for round in self.round_set.all():
            count += round.puzzle_set.count()

        return count
    
    def num_locked(self):
        return self.count_puzzles_of_status(PuzzleStatus.LOCKED)

    def num_solved(self):
        return self.count_puzzles_of_status(PuzzleStatus.SOLVED)
    
    def num_available(self):
        return self.total_puzzles() - self.num_solved() - self.num_locked()
    
    def meta_solves(self):
        count = 0
        for round in self.round_set.all():
            count += round.puzzle_set.filter(status__exact=PuzzleStatus.SOLVED, is_meta__exact=True).count()
        
        return count

class Round(models.Model):
    name = models.CharField(max_length=255)
    hunt = models.ForeignKey(Hunt, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.hunt} - {self.name}"

    def puzzles_ordered(self):
        # TODO: human sort the name? We might have something weird like shell game with numbered puzzles that goes over 10?
        return self.puzzle_set.order_by("-is_meta", "name").all()

class Puzzle(models.Model):
    name = models.CharField(max_length=255)
    hunt_round = models.ForeignKey(Round, on_delete=models.CASCADE)
    url = models.URLField()
    is_meta = models.BooleanField(default=False)
    sheet_id = models.CharField(max_length=255, default="")

    status = models.CharField(max_length=2, choices=PuzzleStatus.choices, default=PuzzleStatus.LOCKED)

    def __str__(self):
        return f"{self.hunt_round} - {self.name}"
    
    def regenerate_puzzle_sheet(self):
        # This won't delete the old sheet, but it will make the site show you the new one.
        self.sheet_id = google.make_puzzle_sheet(f"{self.hunt_round.hunt.name} - {self.name}")
        self.save()

    def sheet_url(self):
        # Make a sheet if one does not exist
        if self.sheet_id == "":
            self.regenerate_puzzle_sheet()
        
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit"


class Answer(models.Model):
    answer_text = models.CharField(max_length=255)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.answer_text}"