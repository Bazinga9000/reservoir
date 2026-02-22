import aiohttp

async def fetch(url):
    '''
    Utility method so that any commands can perform an asynchronous HTTP request
    '''
    async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.content.read()

def tablify(matrix, alignments=None):
    '''
    Convert a multidimensional array into a markdown table:

    If you want the tables columns to be aligned, pass an array of alignments for each row
    -1 = left-aligned
    0 = center-aligned
    1 = right-aligned
    2 = no alignment
    '''
    if matrix == []:
        return ""

    max_len = max(len(i) for i in matrix)

    if alignments is not None:
        for i in alignments:
            if i not in [-1,0,1,2]:
                raise ValueError(f"Alignments must be -1,0,1, or 2, got {i}")
    else:
        alignments = [2 for _ in range(max_len)]

    alignments = [[":---:","---:","---",":---"][i] for i in alignments]

    print(matrix)

    matrix.insert(1, alignments)

    for row in matrix:
        # Escape pipes
        row = [i.replace("|","\\|") for i in row]
                
        # Make all rows equal length
        while len(row) < max_len:
            row.append("")

    return "\n".join("|" + "|".join(row) + "|" for row in matrix)

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