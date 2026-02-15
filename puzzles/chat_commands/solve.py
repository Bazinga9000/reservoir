from .base_command import BaseChatCommand
from ..models import PuzzleStatus, Answer
from channels.db import database_sync_to_async

# TODO: force page to refresh since i think this won't update the form or anything on the page
class SolveCommand(BaseChatCommand):
    def __init__(self):
        super().__init__("solve", "/solve <answer>: Mark a puzzle as solved and add the given answer.")

    async def execute(self, puzzle, args):
        if args == "":
            raise TypeError("/solve must take an answer as argument.")
        
        args = args.upper()

        @database_sync_to_async
        def write():
            puzzle.status = PuzzleStatus.SOLVED
            puzzle.save()

            ans = Answer()
            ans.answer_text = args
            ans.puzzle = puzzle
            ans.save()

        await write()
        return f"{puzzle.name} has been solved with answer **{ args }**"