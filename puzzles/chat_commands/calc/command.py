from ..base_command import BaseChatCommand
from .evaluator import evaluate

import argparse

calc_parser = argparse.ArgumentParser(
    prog = "/calc",
    description = "Do mathematics.",
    add_help = False,
    exit_on_error = False
)

calc_parser.add_argument("expr", nargs="+", help="The expression to evaluate.")


class CalcCommand(BaseChatCommand):
    def __init__(self):
        super().__init__("calc", calc_parser)

    async def execute(self, puzzle, args):
        expr = " ".join(args.expr)
        return f"${evaluate(expr)}$"
        

calce_parser = argparse.ArgumentParser(
    prog = "/calce",
    description = "As /calc, but always converts the result to a float by wrapping it in evalf (e.g 1.414... instead of $\sqrt{2}$)",
    add_help = False,
    exit_on_error = False
)

calce_parser.add_argument("expr", nargs="+", help="The expression to evaluate.")


class CalcECommand(BaseChatCommand):
    def __init__(self):
        super().__init__("calce", calce_parser)

    async def execute(self, puzzle, args):
        expr = "evalf(" + " ".join(args.expr) + ")"
        return f"${evaluate(expr)}$"