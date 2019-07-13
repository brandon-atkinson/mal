#!/usr/bin/env python

import os
import sys
import readline
import reader
import printer
import env
from functools import reduce
from operator import add, sub, mul, floordiv

def _read(line):
    return reader.read_str(line)

def _eval(ast, _env):
    if ast['typ'] != 'lst':
        return eval_ast(ast, _env)
    elif len(ast['val']) == 0:
        return ast
    else:
        ast_nodes = ast['val']
        if ast_nodes[0]['typ'] == 'sym' and ast_nodes[0]['val'] == 'def!':
            #todo: check types of ast nodes
            name = ast_nodes[1]['val']
            val = _eval(ast_nodes[2], _env)
            _env.set(name, val)
            return val
        elif ast_nodes[0]['typ'] == 'sym' and ast_nodes[0]['val'] == 'let*':
            sub_env = env.Env(_env)
            #todo: check types of ast nodes
            bind_lst = ast_nodes[1]['val']
            for di in range(len(bind_lst) // 2):
                i = 2*di
                sub_env.set(bind_lst[i]['val'], _eval(bind_lst[i+1], sub_env))
            return _eval(ast_nodes[2], sub_env)
        elif ast_nodes[0]['typ'] == 'sym' and ast_nodes[0]['val'] == 'do':
            expr_nodes = ast_nodes[1:]
            vals = eval_ast(expr_nodes, _env)
            if len(vals) == 0:
                return {'typ': 'nil', 'val': 'nil'}
            else:
                return vals[-1]
        elif ast_nodes[0]['typ'] == 'sym' and ast_nodes[0]['val'] == 'if':
            cond_expr_node = ast_nodes[1]
            cond_val = eval_ast(cond_expr_node, _env) 
            if cond_val['typ'] != 'nil' and not (cond_val['typ'] == 'bool' and cond_val['val'] == 'false'):
                return eval_ast(ast_nodes[2], _env)
            else:
                if len(ast_nodes) < 4:
                    return {'typ': 'nil', 'val': 'nil'}
                else:
                    return eval_ast(ast_nodes[3], _env)
        else:
            fn, *args = eval_ast(ast, _env)
            val = apply(fn, *args)
            return val

def eval_ast(ast, _env):
    if ast['typ'] == 'sym':
        symbol = ast['val']
        val = _env.get(symbol)
        if val is None:
            raise UndefinedRefError(f"{symbol} not defined")
        else:
            return val
    elif ast['typ'] == 'lst':
        return [_eval(i, _env) for i in ast['val']]
    else:
        return ast

def apply(fn, *args):
    return fn['val'](args)

class UndefinedRefError(Exception):
    pass

def _print(val):
    return printer.pr_str(val, True)

def _add(operands):
    return {'typ': 'int', 'val': reduce(add, [ o['val'] for o in operands ])}

def _sub(operands):
    return {'typ': 'int', 'val': reduce(sub, [ o['val'] for o in operands ])}

def _mul(operands):
    return {'typ': 'int', 'val': reduce(mul, [ o['val'] for o in operands ])}

def _div(operands):
    return {'typ': 'int', 'val': reduce(floordiv, [ o['val'] for o in operands ])}

repl_env = env.Env() 
repl_env.set('nil', {'typ': 'nil', 'val': 'nil'})
repl_env.set('+', {'typ': 'fn', 'val': _add})
repl_env.set('-', {'typ': 'fn', 'val': _sub})
repl_env.set('*', {'typ': 'fn', 'val': _mul})
repl_env.set('/', {'typ': 'fn', 'val': _div})

def rep(inp):
    return _print(_eval(_read(inp), repl_env))

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
