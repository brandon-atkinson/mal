import re

STRING_ESCAPE_PATTERN = re.compile(r'([\n\\"])')

def escape_replacment(match):
    if match[1] == "\n":
        return "\\n"
    else: 
        return "\\" + match[1]

def pr_str(mal, print_readably=False):
    if mal is None:
        return None

    if mal['typ'] == 'lst':
        s = '('
        for i,m in enumerate(mal['val']):
            if i != 0:
                s+= " "
            s += pr_str(m, print_readably) 
        s += ')'
        return s
    elif mal['typ'] == 'nil':
        return mal['val']
    elif mal['typ'] == 'int':
        return str(mal['val'])
    elif mal['typ'] == 'bool':
        return 'true' if mal['val'] else 'false'
    elif mal['typ'] == 'sym':
        return mal['val']
    elif mal['typ'] == 'fn' or mal['typ'] == 'fn*':   
       return "#<function>"
    elif mal['typ'] == 'str':
        val = mal['val']

        if print_readably: 
            val = re.sub(STRING_ESCAPE_PATTERN, escape_replacment, val)
            return '"' + val + '"'
        else: 
            return val
    else:
        raise Exception('unknown type')
