from ..base_command import BaseChatCommand, fetch, tablify
import urllib
import json
import argparse

onelook_parser = argparse.ArgumentParser(
    prog = "/onelook",
    description = "Query [onelook](https://www.onelook.com/) to find words.",
    add_help = False,
    exit_on_error = False,
)
onelook_parser.add_argument("query", nargs="+", help="The query to search.")
onelook_parser.add_argument("-n", "--count", type=int, default=10, help="The maximum number of results to return.")


ONELOOK_URL = "https://api.datamuse.com/words?{params}"

class OneLookCommand(BaseChatCommand):
    def __init__(self):
        super().__init__("onelook", onelook_parser, [
            "ol"
        ])

    async def execute(self, puzzle, args):
        if args.count < 1:
            raise ValueError("Invalid argument: n must be positive.") 

        query = " ".join(args.query)
        top_n = args.count

        defn = None
        if ':' in query:
            split = query.split(':')
            letters = split[0]
            defn = split[1]
        else:
            letters = query

        params = {}
        if letters:
            params['sp'] = letters
        if defn:
            params['ml'] = defn

        url_params = '&'.join([f'{k}={urllib.parse.quote(params[k])}' for k in params.keys()])
        url = ONELOOK_URL.format(params=url_params)

        response = await fetch(url)

        words = [["Result", "Score"]] + [[k['word'], str(k['score'])] for k in json.loads(response)[:top_n]]
        return tablify(words)