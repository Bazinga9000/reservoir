from ..base_command import BaseChatCommand, fetch, tablify
import aiohttp
import json
import argparse


hdas_parser = argparse.ArgumentParser(
    prog = "/hdas",
    description = "Query [util.in](https://util.in/solver) to solve heavy-duty anagrams.",
    epilog = "For information on query syntax, see \n[this page](https://github.com/kevinychen/snap2/wiki/Heavy-duty-anagram-solver).",
    add_help = False,
    exit_on_error = False
)

hdas_parser.add_argument("query", nargs="+", help="The query to search.")
hdas_parser.add_argument("-l", "--lengths", nargs="+", help="A list of known word lengths, e.g \"5 3 4 5\".", type=int)
hdas_parser.add_argument("-f", "--fix_sets", action="store_false", help="Disallow rearrangement of space-separated sets.")
hdas_parser.add_argument("-n", "--count", type=int, default=10, help="The maximum number of results to return.")

HDAS_URL = "https://util.in/api/words/pregex"

class HDASCommand(BaseChatCommand):
    def __init__(self):
        super().__init__("hdas", hdas_parser, [
            "anagram"
        ])

    async def execute(self, puzzle, args):
        if args.count < 1:
            raise ValueError("Invalid argument: n must be positive.") 
        
        query = " ".join(args.query)

        if "\n" in query:
            raise ValueError("Invalid argument: query must not contain a newline.")


        params = {
            "parts": query.split(" "),
            "canRearrange": args.fix_sets,
        }

        if args.lengths:
            params["wordLengths"] = [str(n) for n in args.lengths]

        async with aiohttp.ClientSession() as session:
            async with session.post(HDAS_URL, json=params) as response:
                if response.status != 200:
                    err = response.content.read()
                    raise RuntimeError(str(err))
                else:
                    results = await response.json()
                    table = [["Result", "Score"]] + [(i["message"], "{:.2f}".format(i["score"])) for i in results["results"][:args.count]]
                    return tablify(table)