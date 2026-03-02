from .models import Puzzle, ChatMessage

from .chat_commands import *

REGISTERED_COMMANDS = [
    PingCommand(),
    SolveCommand(),
    OneLookCommand(),
    HDASCommand()
]

def fetch_command_of_name(name):
    for c in REGISTERED_COMMANDS:
        if c.name == name:
            return c
        if name in c.aliases:
            return c
    return None

# Returns another message to send, or None if none 
async def parse_command(chat_message):

    async def make_message(message):
        return await ChatMessage.objects.acreate(
            puzzle=chat_message.puzzle,
            user=None,
            content=message,
            is_system=True
        )


    content = chat_message.content.rstrip()

    # All commands start with slash
    if not content.startswith("/"):
        return None
    
    # Remove leading slash
    content = content[1:]

    # Split command name from args
    content = content.split(" ")
    
    if len(content) == 0:
        content.append("")

    command = content[0]
    args = content[1:]

    # Special case for help to access the various help messages
    if command == "help":
        if args == []:
            return await make_message("\n".join(
                ["/help: List all commands", "/help <command>: Get help for a specific command."] 
                + [i.help_with_aliases() for i in REGISTERED_COMMANDS])
            )
        else:
            c = fetch_command_of_name(args[0])

            if c is None:
                return await make_message(f"Error: no command /{command}. Use /help to list commands.")
            else:
                return await make_message(c.long_help)

    else:
        c = fetch_command_of_name(command)

        if c is None:
            return await make_message(f"Error: no command /{command}. Use /help to list commands.")
        else:
            try:
                out = await c.execute(chat_message.puzzle, c.arg_parser.parse_args(args=args))
                return await make_message(out)
            except Exception as e:
                return await make_message(f"Error: {e}")
