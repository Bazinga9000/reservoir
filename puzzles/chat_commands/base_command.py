


class BaseChatCommand:
    def __init__(self, name, help_description):
        self.name = name
        self.help_description = help_description

    # TODO: this should probably be async
    async def execute(self, puzzle, argument):
        '''
        Do the work required to execute a command. Always accepts the following two arguments:

        puzzle - The puzzle in whose chat this command is being run.
        argument - Everything after the command name, as a string. Complex argument parsing must be done by the command class.

        Return a string for the output of the command, or throw an error
        '''
        raise NotImplementedError(f"Command /{self.name}")