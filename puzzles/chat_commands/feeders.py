from .base_command import BaseChatCommand, tablify
from ..models import PuzzleStatus, Answer
from channels.db import database_sync_to_async
import argparse

feeders_parser = argparse.ArgumentParser(
    prog = "/feeders",
    description = "Get the feeders for this puzzle",
    add_help = False,
    exit_on_error = False
)

class FeedersCommand(BaseChatCommand):
    def __init__(self):
        super().__init__("feeders", feeders_parser)

    async def execute(self, puzzle, args):
        if not puzzle.is_meta:
            return "Error: /feeders only works on metapuzzles"

        @database_sync_to_async
        def read():
          out = [["**Round**", "**Puzzle**", "**Answer**"]]
          for round in puzzle.rounds.all():
              for feeder in round.puzzles_ordered():
                  if not feeder.is_meta:
                      answers = [a.answer_text for a in feeder.answer_set.all()]
                      if answers == []: answers.append("")
                      for answer in answers:
                          out.append([round.name, feeder.name, answer])
          return out
        answers = await read()
        return tablify(answers)
