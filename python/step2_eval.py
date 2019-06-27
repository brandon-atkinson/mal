#!/usr/bin/env python

import os
import sys
import readline
import reader
import printer
from functools import reduce
from operator import add, sub, mul, floordiv

def _read(line):
    return reader.read_str(line)

def _eval(ast, env):
#    print(f"ast={ast}")
    if ast['typ'] != 'lst':
        return eval_ast(ast, env)
    elif len(ast['val']) == 0:
        return ast
    else:
        fn, *args = eval_ast(ast, env)
#        print(f"args={args}")
        val = apply(fn, *args)
#        print(f"{fn}({args}) => {val}")
        return val

def eval_ast(ast, env):
    if ast['typ'] == 'sym':
        symbol = ast['val']
        val = env.get(symbol)
        if val is None:
            raise UndefinedRefError(f"{symbol} not defined")
        else:
            return val
    elif ast['typ'] == 'lst':
        return [_eval(i, env) for i in ast['val']]
    else:
        return ast

def apply(fn, *args):
    return fn['val'](args)

class UndefinedRefError(Exception):
    pass

def _print(val):
    return printer.pr_str(val, True)

def rep(inp):
    repl_env = { 
            '+': {'typ': 'fn', 'val': _add},
            '-': {'typ': 'fn', 'val': _sub},
            '*': {'typ': 'fn', 'val': _mul},
            '/': {'typ': 'fn', 'val': _div} }

    return _print(_eval(_read(inp), repl_env))

def _add(operands):
    return {'typ': 'int', 'val': reduce(add, [ o['val'] for o in operands ])}

def _sub(operands):
    return {'typ': 'int', 'val': reduce(sub, [ o['val'] for o in operands ])}

def _mul(operands):
    return {'typ': 'int', 'val': reduce(mul, [ o['val'] for o in operands ])}

def _div(operands):
    return {'typ': 'int', 'val': reduce(floordiv, [ o['val'] for o in operands ])}

def main(args):
    try: 
        while True:
            try: 
                inp = input("user> ")
                print(rep(inp))
            except Exception as se:
                print("Error: " + str(se))
    except EOFError: 
        sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
