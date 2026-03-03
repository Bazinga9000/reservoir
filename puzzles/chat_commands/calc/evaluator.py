from shunting_yard import shunting_yard
from sympy import *


# (arity, function)
FUNCTIONS = {
    # basic arithmetic
    '+': (2, Add),
    '+u': (1, Abs), # TODO: this is weird, maybe? Not sure how much I like this
    '-': (2, lambda x, y: Add(x, Mul(-1, y))), # yes, this is how sympy does subtraction
    '-u': (1, lambda x: Mul(-1, x)),
    '*': (2, Mul),
    '/': (2, lambda x, y: Mul(x, Pow(y, -1))), # yes, this is how sympy does division
    '^': (2, Pow),

    # Some elementary operations
    'sqrt': (1, sqrt),
    'min': (2, Min),
    'max': (2, Max),
    'abs': (1, Abs),
    'log': (2, log),
    'ln': (1, log),

    # constants
    'pi': (0, lambda: pi),
    'e': (0, lambda: E),
    'i': (0, lambda: I),

    # trig
    'sin': (1, sin),
    'cos': (1, cos),
    'tan': (1, tan),
    'sec': (1, sec),
    'csc': (1, csc),
    'cot': (1, cot),
    'asin': (1, asin),
    'acos': (1, acos),
    'atan': (1, atan),
    'asec': (1, asec),
    'acsc': (1, acsc),
    'acot': (1, acot),
    
    # hyperbolic trig
    'sinh': (1, sinh),
    'cosh': (1, cosh),
    'tanh': (1, tanh),
    'sech': (1, sech),
    'csch': (1, csch),
    'coth': (1, coth),
    'asinh': (1, asinh),
    'acosh': (1, acosh),
    'atanh': (1, atanh),
    'asech': (1, asech),
    'acsch': (1, acsch),
    'acoth': (1, acoth),

    # symbols
    'x': (0, lambda: Symbol('x')),
    'y': (0, lambda: Symbol('y')),
    'z': (0, lambda: Symbol('z')),
    'infinity': (0, lambda: oo),

    # calculus
    'integrate': (2, integrate),
    'integral': (2, integrate),    
    'definite_integral': (4, lambda f,x,a,b: integrate(f, (x,a,b))),
    'derivative': (2, Derivative),
    'diff': (2, Derivative),

    # special functions
    'erf': (1, erf),
    'erfi': (1, erfi),
    'gamma': (1, gamma),
    'factorial': (1, factorial),

    # symbolic manipulation
    'simplify': (1, simplify),
    'factor': (1, factor),
    'expand': (1, expand),
    'subs': (3, lambda x,y,z: x.subs(y,z)), # TODO: if we support variadic functions, allow simultaneous substittuion like subs(xy, x, 1, y, 2)
    'evalf': (1, lambda x: x.evalf()),
}


# TODO: maybe migrate to our own RPN parser, since shunting-yard doesn't check arities at parse time, so something like sin(1, 2) will not error meaningfully
# should just be a simple matter of pushing the requested arity along with the function onto the stack and writing an arity-checking metafunction for all
# the simple stuff
# this should do for now as a starting point

def evaluate(formula):
    parse = shunting_yard(formula).split(" ")

    stack = []


    for token in parse:
        if token[0] in '0123456789.': # this is a number
            if '.' in token: # this is a float
                stack.append(Float(token))
            else:
                stack.append(Integer(token))
        else:
            if token not in FUNCTIONS:
                raise ValueError(f"Function {token} not found")
            
            arity, f = FUNCTIONS[token]

            if len(stack) < arity:
                raise ValueError(f"Function {token} expected {arity} arguments, got {len(stack)}.")

            args = []
            for _ in range(arity):
                args.append(stack.pop())
            args.reverse()
            stack.append(f(*args))

    if len(stack) != 1:
        raise ValueError(f"Output stack too large. You passed a function too many arguments.")

    out = stack[0]
    
    return latex(out)