from .base_command import BaseChatCommand
import argparse

# A do-nothing argparser
ping_parser = argparse.ArgumentParser(
    prog = "/ping",
    description = "Ping the server.",
    add_help = False,
    exit_on_error = False,
)

class PingCommand(BaseChatCommand):
    def __init__(self):
        super().__init__("ping", ping_parser)

    async def execute(self, puzzle, args):
        return "Pong!"