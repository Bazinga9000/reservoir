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
    def __init__(self, name, arg_parser, aliases=[]):
        self.name = name
        self.arg_parser = arg_parser
        self.aliases = aliases

        assert self.arg_parser.add_help == False
        assert self.arg_parser.exit_on_error == False

    async def execute(self, puzzle, args):
        '''
        Do the work required to execute a command. Always accepts the following two arguments:

        puzzle - The puzzle in whose chat this command is being run.
        args - The result of parsing the command's arguments with argparse.

        Return a string for the output of the command, or throw an error
        '''
        raise NotImplementedError(f"Command /{self.name} does not have an implemented `execute` method.")
    
    @property
    def short_help(self):
        return f"/{self.name}: {self.arg_parser.description}"

    @property
    def long_help(self):
        return self.arg_parser.format_help()

    def help_with_aliases(self):
        if self.aliases == []:
            return self.short_help
        else:
            alias_strings = "\n".join([f"/{a}: Alias for /{self.name}" for a in self.aliases])
            return f"{self.short_help}\n{alias_strings}"