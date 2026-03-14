from ..base_command import BaseChatCommand, fetch, tablify
import urllib
import json
import argparse

sajak_parser = argparse.ArgumentParser(
    prog = "/sajak",
    description = "Query [Sajak](https://www.github.com/Bazinga9000/sajak/) to find words.",
    add_help = False,
    exit_on_error = False,
)
sajak_parser.add_argument("query", nargs="+", help="The query to search.")
sajak_parser.add_argument("-n", "--count", type=int, default=10, help="The maximum number of results to return.")


SAJAK_URL = "http://localhost:1983/query"

class SajakCommand(BaseChatCommand):
    def __init__(self):
        super().__init__("sajak", sajak_parser, [
            "s", "nutrimatic", "n"
        ])

    async def execute(self, puzzle, args):
        if args.count < 1:
            raise ValueError("Invalid argument: n must be positive.") 

        query = " ".join(args.query)
        top_n = args.count


        params = {}
        params["query"] = query
        params["max_results"] = top_n

        response = await fetch(SAJAK_URL, json=params)

        words = [["Result", "Score"]] + [[k['result'], "{:.2f}".format(k['score'])] for k in json.loads(response)[:top_n]]
        return tablify(words)