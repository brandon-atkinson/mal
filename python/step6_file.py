#!/usr/bin/env python

import os
import sys
import readline
import reader
import printer
import env
import core

def _read(line):
    return reader.read_str(line)

# what is the difference between _eval and eval_ast?
# same signature fn(ast, env.Env)
# they are not, they interacted to break up the recursion
# refactoring to make single recursive function more understandable

def _eval(ast, _env):
    while True:
        if ast['typ'] == 'lst':
            if len(ast['val']) == 0:
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

                    ast = ast_nodes[2]
                    _env = sub_env
                    continue
                elif ast_nodes[0]['typ'] == 'sym' and ast_nodes[0]['val'] == 'do':
                    for a in ast_nodes[1:-1]:
                        val = _eval(a, _env)

                    ast = ast_nodes[-1]
                    continue
                elif ast_nodes[0]['typ'] == 'sym' and ast_nodes[0]['val'] == 'if':
                    cond = _eval(ast_nodes[1], _env)

                    if (cond['typ'] == 'nil' or (cond['typ'] == 'bool' and cond['val'] == False)):
                        if len(ast_nodes) > 3: 
                            ast = ast_nodes[3]
                        else: 
                            ast = {'typ':'nil', 'val': 'nil'}
                    else:
                        ast = ast_nodes[2]

                    continue
                elif ast_nodes[0]['typ'] == 'sym' and ast_nodes[0]['val'] == 'fn*':
                    fn_params = [ p['val'] for p in ast_nodes[1]['val'] ]
                    fn_body = ast_nodes[2]
                    fn_env = _env

                    def fn(*exprs):
                        return _eval(fn_body, env.Env(fn_env, fn_params, list(exprs)))

                    return {'typ': 'fn*', 
                            'val': {
                                'env': fn_env, 
                                'params': fn_params, 
                                'ast': fn_body, 
                                'fn': {
                                    'typ': 'fn', 
                                    'val': fn}}}
                else:
                    fn, *args = [_eval(a, _env) for a in ast['val']]

                    #tail-call optimization
                    if fn['typ'] == 'fn': 
                        return fn['val'](*args)
                    else:
                        fnv = fn['val']

                        ast = fnv['ast']
                        _env = env.Env(fnv['env'], fnv['params'], list(args))
                        continue

        elif ast['typ'] == 'sym':
            symbol = ast['val']
            val = _env.get(symbol)
            if val is None:
                raise UndefinedRefError(f"{symbol} not defined")
            else:
                return val
        else:
            return ast

class UndefinedRefError(Exception):
    pass

def _print(val):
    return printer.pr_str(val, True)


repl_env = env.Env() 
for name, fn in core.ns.items():
    repl_env.set(name, fn)

def _eval_fn(ast):
    return _eval(ast, repl_env)

repl_env.set('eval', {'typ': 'fn', 'val': _eval_fn})

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
