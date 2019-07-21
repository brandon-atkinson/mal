from functools import reduce
from operator import add, sub, mul, floordiv, lt, le, gt, ge
from printer import pr_str
from reader import read_str

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

def _read_string(mal_str):
    read_str(mal_str['val'])

def _slurp(filename):
    with open(filename['val']) as f:
        return {'typ': 'str', 'val':f.read()}

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
        'read-string': {'typ': 'fn', 'val':_read_string},
        'slurp': {'typ': 'fn', 'val':_slurp},
        }
