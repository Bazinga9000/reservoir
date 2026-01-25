from django.db import models

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
    
    def num_avaliable(self):
        return self.total_puzzles() - self.num_solved() - self.num_locked()

class Round(models.Model):
    name = models.CharField(max_length=255)
    hunt = models.ForeignKey(Hunt, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.hunt} - {self.name}"

class Puzzle(models.Model):
    name = models.CharField(max_length=255)
    hunt_round = models.ForeignKey(Round, on_delete=models.CASCADE)
    url = models.URLField()

    status = models.CharField(max_length=2, choices=PuzzleStatus.choices, default=PuzzleStatus.LOCKED)

    def __str__(self):
        return f"{self.hunt_round} - {self.name}"
    

class Answer(models.Model):
    answer_text = models.CharField(max_length=255)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.answer_text}"