from .base_command import BaseChatCommand, tablify
from ..models import PuzzleStatus, Answer, TagKind, Tag
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
import argparse

feeders_parser = argparse.ArgumentParser(
    prog = "/feeders",
    description = "Get the feeders for this puzzle",
    add_help = False,
    exit_on_error = False
)
feeders_parser.add_argument("--all", action="store_true", help="Get all non-puzzles in all rounds this meta is attached to, regardless of feeder-for tags.")

class FeedersCommand(BaseChatCommand):
    def __init__(self):
        super().__init__("feeders", feeders_parser)

    async def execute(self, puzzle, args):
        if not puzzle.is_meta:
            return "Error: /feeders only works on metapuzzles"

        @database_sync_to_async
        def read():
            out = [["**Round**", "**Puzzle**", "**Answer**"]]
            rounds = puzzle.tags.filter(tag__kind=TagKind.META).all()

            feeders = set()

            for round_tag in puzzle.tags.filter(tag__kind=TagKind.META).all():
                if args.all:
                    for feeder in round_tag.puzzles_ordered():
                        if not feeder.is_meta:
                            feeders.add(feeder)
                try:
                    feeder_tag = Tag.objects.get(kind=TagKind.FEEDER, name=round_tag.name)
                    feeders.update(*feeder_tag.puzzle_set.all())
                except ObjectDoesNotExist:
                    print(f"No feeder tag for {round_tag}?")
            return out
        answers = await read()
        return tablify(answers)
