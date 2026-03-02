from .base_command import BaseChatCommand
from ..models import PuzzleStatus, Answer
from channels.db import database_sync_to_async
import argparse

solve_parser = argparse.ArgumentParser(
    prog = "/solve",
    description = "Mark this puzzle solved with the given answer.",
    add_help = False,
    exit_on_error = False
)

solve_parser.add_argument("answer", nargs="+", help="The answer to add to the puzzle")


# TODO: force page to refresh since i think this won't update the form or anything on the page
class SolveCommand(BaseChatCommand):
    def __init__(self):
        super().__init__("solve", solve_parser)

    async def execute(self, puzzle, args):
        answer = " ".join(args.answer).upper()

        @database_sync_to_async
        def write():
            puzzle.status = PuzzleStatus.SOLVED
            puzzle.save()

            ans = Answer()
            ans.answer_text = answer
            ans.puzzle = puzzle
            ans.save()

        await write()
        return f"{puzzle.name} has been solved with answer **{ answer }**"