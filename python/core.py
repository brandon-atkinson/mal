from functools import reduce
from operator import add, sub, mul, floordiv, lt, le, gt, ge
from printer import pr_str
from reader import read_str
import env
from collections import deque

NIL = {'typ':'nil', 'val': 'nil'}
TRUE = {'typ':'bool', 'val': True}
FALSE = {'typ':'bool', 'val': False}

def mal_sym(val):
    return {'typ': 'sym', 'val': val}

def mal_bool(val):
    if val: 
        return TRUE
    else:
        return FALSE

def mal_int(val):
    return {'typ': 'int', 'val': val}

def mal_str(val):
    return {'typ': 'str', 'val': val}

def mal_atom(mal):
    return {'typ': 'atom', 'val': mal}

def mal_list(*operands):
    return {'typ': 'lst', 'val': [*operands]}

def mal_fn(fn):
    return {'typ': 'fn', 'val': fn}

def mal_closure(env, params, ast, native_fn):
    return {'typ': 'fn*', 
            'val': { 
                'env': env, 
                'params': params, 
                'ast': ast, 
                'fn': { 'typ': 'fn', 'val': native_fn}}}

def mal_val(mal):
    return mal['val']

def mal_set_val(mal, val):
    mal['val', val]

def mal_type(mal):
    return mal['typ']

def mal_types_eq(mal1, mal2):
    return mal_type(mal1) == mal_type(mal2)

def mal_is_nil(mal):
    return mal == NIL

def mal_is_sym(mal):
    return mal['typ'] == 'sym'

def mal_is_bool(mal):
    return mal['typ'] == 'bool'

def mal_is_int(mal):
    return mal['typ'] == 'int'

def mal_is_str(mal):
    return mal['typ'] == 'str'

def mal_is_atom(mal):
    return mal['typ'] == 'atom'

def mal_is_list(mal):
    return mal['typ'] == 'lst'

def mal_is_empty(mal):
    return mal_is_list(mal) and len(mal_val(mal)) == 0 

def mal_is_fn(mal):
    return mal['typ'] == 'fn'

def _add(*operands):
    return mal_int(reduce(add, [ o['val'] for o in operands ]))

def _sub(*operands):
    return mal_int(reduce(sub, [ o['val'] for o in operands ]))

def _mul(*operands):
    return mal_int(reduce(mul, [ o['val'] for o in operands ]))

def _div(*operands):
    return mal_int(reduce(floordiv, [ o['val'] for o in operands ]))

def _prn(arg):
    val = pr_str(arg, print_readably=True)
    print(val)
    return NIL

def _is_list(arg):
    return mal_bool(mal_is_list(arg))

def _is_empty(lst):
    return mal_bool(len(mal_val(lst)) == 0)

def _count(lst):
    if mal_is_nil(lst):
        cnt = 0
    else:
        cnt = len(mal_val(lst))
    return mal_int(cnt)

def _eq(a, b):
    a_val = mal_val(a)
    b_val = mal_val(b)

    if mal_types_eq(a, b):
        if mal_is_list(a):
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

    return mal_bool(eq)

def _lt(a, b):
    return mal_bool(lt(mal_val(a),mal_val(b)))

def _le(a, b):
    return mal_bool(le(mal_val(a),mal_val(b)))

def _gt(a, b):
    return mal_bool(gt(mal_val(a),mal_val(b)))

def _ge(a, b):
    return mal_bool(ge(mal_val(a),mal_val(b)))

def _pr_str(*ast):
    s = str.join(" ", [ pr_str(a, print_readably=True) for a in ast ])
    return mal_str(s)

def _str(*lst):
    s = str.join('', [ pr_str(ast, print_readably=False) for ast in lst ])
    return mal_str(s)

def _prn(*lst):
    s = _join_str(" ", *[ _pr_str(i) for i in lst ])
    print(mal_val(s))
    return NIL

def _join_str(sep, *strs):
    joined = ""

    for s in strs: 
        if not mal_is_str(s):
            raise ValueError("passed non-str")

        joined = str.join(sep, [ mal_val(s) for s in strs ])

    return mal_str(joined)

def _println(*lst):
    s = _join_str(" ", *[_str(i) for i in lst])
    print(mal_val(s))
    return NIL

def _read_string(s):
    return read_str(mal_val(s))

def _slurp(filename):
    with open(mal_val(filename)) as f:
        return mal_str(f.read())

def _is_atom(mal):
    return mal_bool(mal_is_atom(mal))

def _deref_atom(atom):
    return mal_val(atom)

def _reset_atom(atom, mal):
    atom['val'] = mal
    return mal

def mal_is_pair(mal):
    return mal_is_list(mal) and not mal_is_empty(mal)

def _quasiquote(ast):
    if not mal_is_pair(ast):
        return mal_list(mal_sym('quote'), ast)
    else:
        lst = mal_val(ast)
        if mal_is_sym(lst[0]) and mal_val(lst[0]) == 'unquote':
            return lst[1]
        
        if mal_is_pair(lst[0]):
            sub_lst = mal_val(lst[0]) 
            if mal_is_sym(sub_lst[0]) and mal_val(sub_lst[0]) == 'splice-unquote':
                retval = mal_list(mal_sym('concat'), sub_lst[1], _quasiquote(mal_list(*lst[1:]))) 
                return retval

        return mal_list(mal_sym('cons'), _quasiquote(lst[0]), _quasiquote(mal_list(*lst[1:])))

def _eval(ast, _env):
    while True:
        if mal_is_list(ast):
            if len(mal_val(ast)) == 0:
                return ast
            else:
                ast_nodes = mal_val(ast)

                first = ast_nodes[0]

                if mal_is_sym(first) and mal_val(first) == 'quote':
                    return ast_nodes[1]
                elif mal_is_sym(first) and mal_val(first) == 'def!':
                    #todo: check types of ast nodes
                    name = mal_val(ast_nodes[1])
                    val = _eval(ast_nodes[2], _env)
                    _env.set(name, val)
                    return val
                if mal_is_sym(first) and mal_val(first) == 'quasiquote':
                    ast = _quasiquote(ast_nodes[1])    
                    continue
                elif mal_is_sym(first) and mal_val(first) == 'let*':
                    sub_env = env.Env(_env)
                    #todo: check types of ast nodes
                    bind_lst = mal_val(ast_nodes[1])
                    for di in range(len(bind_lst) // 2):
                        i = 2*di
                        sub_env.set(mal_val(bind_lst[i]), _eval(bind_lst[i+1], sub_env))

                    ast = ast_nodes[2]
                    _env = sub_env
                    continue
                elif mal_is_sym(first) and mal_val(first) == 'do':
                    for a in ast_nodes[1:-1]:
                        val = _eval(a, _env)

                    ast = ast_nodes[-1]
                    continue
                elif mal_is_sym(first) and mal_val(first) == 'if':
                    cond = _eval(ast_nodes[1], _env)

                    if (mal_is_nil(cond) or (mal_is_bool(cond) and mal_val(cond) == False)):
                        if len(ast_nodes) > 3: 
                            ast = ast_nodes[3]
                        else: 
                            ast = NIL
                    else:
                        ast = ast_nodes[2]

                    continue
                elif mal_is_sym(first) and mal_val(first) == 'fn*':
                    fn_params = [ mal_val(p) for p in mal_val(ast_nodes[1]) ]
                    fn_body = ast_nodes[2]
                    fn_env = _env

                    def fn(*exprs):
                        return _eval(fn_body, env.Env(fn_env, fn_params, list(exprs)))

                    return mal_closure(fn_env, fn_params, fn_body, fn)
                else:
                    fn, *args = [_eval(a, _env) for a in mal_val(ast)]

                    #tail-call optimization
                    if mal_is_fn(fn): 
                        return mal_val(fn)(*args)
                    else:
                        fnv = mal_val(fn)

                        ast = fnv['ast']
                        _env = env.Env(fnv['env'], fnv['params'], list(args))
                        continue

        elif mal_is_sym(ast):
            symbol = mal_val(ast)
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
        if mal_is_list(item):
            _unprocessed.extendleft(list(reversed(mal_val(item))))
        else: 
            flat_list.append(item)
    
    return mal_list(flat_list)

def _cons(first, rest):
    new_lst = [first, *mal_val(rest)]
    return mal_list(*new_lst)

def _car(lst):
    vals = mal_val(lst)
    if len(vals) == 0:
        raise ValueError("expected pair")
    else:
        return vals[0]

def _cdr(lst):
    vals = mal_val(lst)
    if len(vals) == 0:
        raise ValueError("expected pair")
    else:
        return mal_list(*vals[1:])

def _nth(lst, n):
    idx = mal_val(n)
    vals = mal_val(lst)

    if idx < 0 or idx > len(lst):
        raise ValueError("index out of range")

    return vals[mal_val(n)]

def _concat(*lsts):
    new_lst = []

    for lst in lsts:
        new_lst.extend(mal_val(lst))

    return mal_list(*new_lst)

ns = {
        '+': mal_fn(_add),
        '-': mal_fn(_sub),
        '*': mal_fn(_mul),
        '/': mal_fn(_div),
        'prn': mal_fn(_prn),
        'list': mal_fn(mal_list),
        'list?': mal_fn(_is_list),
        'empty?': mal_fn(_is_empty),
        'count': mal_fn(_count),
        '=': mal_fn(_eq),
        '<': mal_fn(_lt),
        '<=': mal_fn(_le),
        '>': mal_fn(_gt),
        '>=': mal_fn(_ge),
        'not': eval(read_str("(fn* (c) (if c false true))")),
        'pr-str': mal_fn(_pr_str),
        'str': mal_fn(_str),
        'prn': mal_fn(_prn),
        'println': mal_fn(_println),
        'read-string': mal_fn(_read_string),
        'slurp': mal_fn(_slurp),
        'atom': mal_fn(mal_atom),
        'atom?': mal_fn(_is_atom),
        'deref': mal_fn(_deref_atom),
        'reset!': mal_fn(_reset_atom),
        'flatten': mal_fn(_flatten),
        'apply': mal_fn(_apply),
        'swap!': eval(read_str("(fn* (atm fn & args) (reset! atm (apply fn (deref atm) args)))")),
        'eval': mal_fn(eval),
        'cons': mal_fn(_cons),
        'car': mal_fn(_car),
        'first': mal_fn(_car),
        'cdr': mal_fn(_cdr),
        'rest': mal_fn(_cdr),
        'nth': mal_fn(_nth),
        'concat': mal_fn(_concat),
        }

for name, fn in ns.items():
    _env.set(name, fn)
