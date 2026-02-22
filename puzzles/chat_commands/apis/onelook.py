from ..base_command import BaseChatCommand, fetch, tablify
import shlex
import urllib
import json

ONELOOK_URL = "https://api.datamuse.com/words?{params}"

class OneLookCommand(BaseChatCommand):
    def __init__(self):
        super().__init__("onelook", "/onelook <query> <optional n>: Query onelook for the top `n` words matching `query`.", [
            "ol"
        ])

    async def execute(self, puzzle, args):
        args = shlex.split(args)

        if len(args) == 1:
            args.append("10") # Default n

        if len(args) != 2:
            raise TypeError("/onelook must take one or two arguments.")
        
        query = args[0]
        try:
            top_n = int(args[1])
        except: 
            raise ValueError("Invalid argument: n must be an integer.")
        
        if top_n < 1:
            raise ValueError("Invalid argument: n must be positive.") 


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