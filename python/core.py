from functools import reduce
from operator import add, sub, mul, floordiv, lt, le, gt, ge
from printer import pr_str
from reader import read_str
import env
from collections import deque

def _add(*operands):
    return {'typ': 'int', 'val': reduce(add, [ o['val'] for o in operands ])}

def _sub(*operands):
    return {'typ': 'int', 'val': reduce(sub, [ o['val'] for o in operands ])}

def _mul(*operands):
    return {'typ': 'int', 'val': reduce(mul, [ o['val'] for o in operands ])}

def _div(*operands):
    return {'typ': 'int', 'val': reduce(floordiv, [ o['val'] for o in operands ])}

def _prn(arg):
    val = pr_str(arg, print_readably=True)
    print(val)
    return {'typ':'nil', 'val':'nil'}

def _list(*operands):
    return {'typ':'lst', 'val': [*operands]}

def _islist(arg):
    return {'typ':'bool', 'val': arg['typ'] == 'lst'}

def _isempty(lst):
    return {'typ':'bool', 'val': len(lst['val']) == 0}

def _count(lst):
    if lst['typ'] == 'nil':
        cnt = 0
    else:
        cnt = len(lst['val'])
    return {'typ':'int', 'val': cnt}

def _eq(a, b):
    a_typ = a['typ']
    a_val = a['val']
    b_typ = b['typ']
    b_val = b['val']

    if a_typ == b_typ:
        if a_typ == 'lst':
            if len(a_val) == len(b_val):
                eq = True
                for i in range(len(a_val)):
                    eq = eq and _eq(a_val[i], b_val[i])
            else:
                eq = False
        else:
            eq = a_val == b_val
    else:
        eq = False

    return {'typ':'bool', 'val': eq}

def _lt(a, b):
    return {'typ':'bool', 'val': lt(a['val'],b['val'])}

def _le(a, b):
    return {'typ':'bool', 'val': le(a['val'],b['val'])}

def _gt(a, b):
    return {'typ':'bool', 'val': gt(a['val'],b['val'])}

def _ge(a, b):
    return {'typ':'bool', 'val': ge(a['val'],b['val'])}

def _pr_str(*ast):
    s = str.join(" ", [ pr_str(a, print_readably=True) for a in ast ])
    return {'typ': 'str', 'val': s}

def _str(*lst):
    s = str.join('', [ pr_str(ast, print_readably=False) for ast in lst ])
    return {'typ': 'str', 'val': s}

def _prn(*lst):
    s = _join_str(" ", *[ _pr_str(i) for i in lst ])
    print(s['val'])
    return {'typ': 'nil', 'val':'nil'}

def _join_str(sep, *strs):
    joined = ""

    for s in strs: 
        if s['typ'] != 'str':
            raise "passed non-str"

        joined = str.join(sep, [ s['val'] for s in strs ])

    return {'typ': 'str', 'val': joined}

def _println(*lst):
    s = _join_str(" ", *[_str(i) for i in lst])
    print(s['val'])
    return {'typ': 'nil', 'val': 'nil'}

def _read_string(mal_str):
    return read_str(mal_str['val'])

def _slurp(filename):
    with open(filename['val']) as f:
        return {'typ': 'str', 'val':f.read()}

def _atom(mal):
    return {'typ':'atom', 'val': mal}

def _is_atom(mal):
    return {'typ': 'bool', 'val':  mal['typ'] == 'atom'}

def _deref_atom(atom):
    return atom['val']

def _reset_atom(atom, mal):
    atom['val'] = mal
    return mal

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

_env = env.Env()

def eval(ast):
    return _eval(ast, _env)

def _apply(fn, *args):
    return eval(_flatten(fn, *args))

def _flatten(*args):
    flat_list = []
    _unprocessed = deque(args)

    while len(_unprocessed) > 0: 
        item = _unprocessed.popleft()
        if item['typ'] == 'lst':
            _unprocessed.extendleft(list(reversed(item['val'])))
        else: 
            flat_list.append(item)
    
    return {'typ': 'lst', 'val': flat_list}

ns = {
        '+': {'typ': 'fn', 'val': _add},
        '-': {'typ': 'fn', 'val': _sub},
        '*': {'typ': 'fn', 'val': _mul},
        '/': {'typ': 'fn', 'val': _div},
        'prn': {'typ': 'fn', 'val': _prn},
        'list': {'typ': 'fn', 'val': _list},
        'list?': {'typ': 'fn', 'val': _islist},
        'empty?': {'typ': 'fn', 'val': _isempty},
        'count': {'typ': 'fn', 'val': _count},
        '=': {'typ': 'fn', 'val': _eq},
        '<': {'typ': 'fn', 'val': _lt},
        '<=': {'typ': 'fn', 'val': _le},
        '>': {'typ': 'fn', 'val': _gt},
        '>=': {'typ': 'fn', 'val': _ge},
        'not': eval(read_str("(fn* (c) (if c false true))")),
        'pr-str': {'typ': 'fn', 'val': _pr_str},
        'str': {'typ': 'fn', 'val': _str},
        'prn': {'typ': 'fn', 'val': _prn},
        'println': {'typ': 'fn', 'val': _println},
        'read-string': {'typ': 'fn', 'val': _read_string},
        'slurp': {'typ': 'fn', 'val': _slurp},
        'atom': {'typ': 'fn', 'val': _atom},
        'atom?': {'typ': 'fn', 'val': _is_atom},
        'deref': {'typ': 'fn', 'val': _deref_atom},
        'reset!': {'typ': 'fn', 'val': _reset_atom},
        'flatten': {'typ': 'fn', 'val': _flatten},
        'apply': {'typ': 'fn', 'val': _apply},
        'swap!': eval(read_str("(fn* (atm fn & args) (reset! atm (apply fn (deref atm) args)))")),
        'eval':{'typ': 'fn', 'val': eval},
        }

for name, fn in ns.items():
    _env.set(name, fn)
