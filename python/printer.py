def pr_str(mal, print_readably=False):
    if mal is None:
        return None
    if type(mal) is list:
        s = '('
        for i,m in enumerate(mal):
            if i != 0:
                s+= " "
            s += pr_str(m) 
        s += ')'
        return s
    elif type(mal) is dict: 
        if mal['typ'] == 'int':
            return str(mal['val'])
        elif mal['typ'] == 'bool':
            return mal['val']
        elif mal['typ'] == 'sym':
            return mal['val']
        elif mal['typ'] == 'str':
            val = mal['val']

            if print_readably: 
                val = val.replace(r'\n', "\n") 
                val = val.replace(r'\r', "\r") 
                val = val.replace('\\\\', '\\') 
                return f'"{val}"'
            else: 
                return f'"{val}"'

    raise Exception('unknown type')

    
def test_pr_str():
    assert pr_str([{'typ':'sym','val':'hi'}]) == '(hi)'
    assert pr_str([{'typ':'sym','val':'bye'},[{'typ':'int','val':25}]]) == '(bye (25))'
