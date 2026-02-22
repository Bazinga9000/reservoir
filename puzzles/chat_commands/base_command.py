


class BaseChatCommand:
    def __init__(self, name, help_description, aliases=[]):
        self.name = name
        self.help_description = help_description
        self.aliases = aliases

    async def execute(self, puzzle, argument):
        '''
        Do the work required to execute a command. Always accepts the following two arguments:

        puzzle - The puzzle in whose chat this command is being run.
        argument - Everything after the command name, as a string. Complex argument parsing must be done by the command class.

        Return a string for the output of the command, or throw an error
        '''
        raise NotImplementedError(f"Command /{self.name} does not have an implemented `execute` method.")
    
    def help_with_aliases(self):
        if self.aliases == []:
            return self.help_description
        else:
            alias_strings = "\n".join([f"/{a}: Alias for /{self.name}" for a in self.aliases])
            return f"{self.help_description}\n{alias_strings}"