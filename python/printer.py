def pr_str(mal, print_readably=False):
    if mal is None:
        return None

    if mal['typ'] == 'lst':
        s = '('
        for i,m in enumerate(mal['val']):
            if i != 0:
                s+= " "
            s += pr_str(m) 
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
    elif mal['typ'] == 'fn':
       return "#<function>"
    elif mal['typ'] == 'str':
        val = mal['val']

        if print_readably: 
            val = val.replace(r'\n', "\n") 
            val = val.replace(r'\r', "\r") 
            val = val.replace('\\\\', '\\') 
            return f'"{val}"'
        else: 
            return f'"{val}"'
    else:
        raise Exception('unknown type')
