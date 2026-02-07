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

    # Return the starting priority value of a puzzle type
    @staticmethod
    def default_priority(status):
        if status == PuzzleStatus.LOCKED:
            return 0.2 # This is nonzero to account for locked metas
        elif status == PuzzleStatus.NOT_STARTED:
            return 1.3
        elif status == PuzzleStatus.IN_PROGRESS:
            return 1
        elif status == PuzzleStatus.STUCK:
            return 1.75
        elif status == PuzzleStatus.NES:
            return 2
        elif status == PuzzleStatus.SOLVED:
            return 0

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
    
    def top_prio_puzzles(self):
        puzzle_max = 10
        puzzles = self.puzzle_set.filter(~models.Q(status__exact=PuzzleStatus.SOLVED)).all()[:puzzle_max]
        return sorted(puzzles, key=(lambda p: (-p.priority(), p.name)))
        

class Round(models.Model):
    name = models.CharField(max_length=255)
    hunt = models.ForeignKey(Hunt, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    def puzzles_ordered(self):
        # TODO: human sort the name? We might have something weird like shell game with numbered puzzles that goes over 10?
        return self.puzzle_set.order_by("-is_meta", "name").all()
    
    # An extra multiplier on the puzzles of this round based on its meta structure
    def priority_multiplier(self):
        num_metas = self.puzzle_set.filter(is_meta=True).count()

        # This round has no metas, no adjustment
        if num_metas == 0:
            return 1
        
        solved_metas = self.puzzle_set.filter(models.Q(is_meta=True) and ~models.Q(status=PuzzleStatus.SOLVED)).count()
        unsolved_metas = num_metas - solved_metas

        # This round has metas, but all of them are solved, so we lower the round's priority
        if unsolved_metas == 0:
            return 0.25 # Nonzero in case a feeder used elsewhere is prioritized
        
        # This round has exactly one unsolved meta and no other metas. Give it massive priority. 
        if num_metas == unsolved_metas and num_metas == 1:
            return 10
        
        # TODO: if we ever explicitly enable setting puzzles as feeders to metas, account for that
        num_feeders = self.puzzle_set.filter(is_meta=False).count()

        # This round has only metas. It's probably *extremely* important. Give it brobdingnagian priority.
        if num_feeders == 0:
            return 50

        # This round has multiple metas and some non-meta feeders and thus something weird is going on. 
        # It is not quite as important as a feederless round, but still more important than a 1 meta round
        # so we give it a merely falstaffian priority 
        return 25


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
    
    def priority(self):
        # Solved puzzles have 0 priority, no need to do any further math
        if self.status == PuzzleStatus.SOLVED:
            return 0
        
        priority = PuzzleStatus.default_priority(self.status)

        for hunt_round in self.rounds.all():
            priority *= hunt_round.priority_multiplier()

        # Metas are highly prioritized above and beyond their round multipliers
        if self.is_meta:
            priority *= 10

        # An unsolved puzzle with answers??? How strange. Give it a priority boost.
        if self.answer_set.count() > 0:
            priority *= 1.5

        return priority


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