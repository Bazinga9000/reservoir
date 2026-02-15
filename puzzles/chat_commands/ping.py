from .base_command import BaseChatCommand

class PingCommand(BaseChatCommand):
    def __init__(self):
        super().__init__("ping", "/ping: Ping the server.")

    async def execute(self, puzzle, args):
        return "Pong!"