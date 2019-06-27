import re

class Reader:

    def __init__(self, tokens):
        self.tokens = tokens.copy()
        self.position = 0

    def next(self):
        if self.position < len(self.tokens):
            t = self.tokens[self.position]
            self.position += 1
        else:
            t = None

        return t

    def peek(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        else:
            return None

def test_reader_init():
    r = Reader([])
    assert True

def test_reader_next():
    r = Reader(['(','next',')'])
    assert r.next() == '('
    assert r.next() == 'next'
    assert r.next() == ')'
    assert r.next() is None

def test_reader_peek():
    r = Reader(['(','peek',')'])
    assert r.peek() == '('
    assert r.peek() == '('
    assert r.next() == '('
    assert r.peek() == 'peek'
    assert r.peek() == 'peek'
    assert r.next() == 'peek'
    assert r.peek() == ')'
    assert r.peek() == ')'
    assert r.next() == ')'
    assert r.peek() is None
    assert r.next() is None

def read_str(s):
    r = Reader(tokenize(s))
    return read_form(r)

TOKEN_PATTERN = re.compile(r'''[\s,]*(~@|[\[\]{}()'`~^@]|"(?:\\.|[^\\"])*"?|;.*|[^\s\[\]{}('"`,;)]*)''')

def tokenize(s):
    return [t for t in TOKEN_PATTERN.findall(s) if t != '']
    
def test_tokenize():
    tokens = tokenize("(sum      1 2\n)")
    assert tokens == ['(', 'sum', '1', '2', ')']

def read_form(reader):
    token = reader.peek()

    if token is None:
        form = None
    elif token == '(' :
        form = read_list(reader)
    else:
        form = read_atom(reader)

    return form

def read_list_form(reader):
    token = reader.peek()

    if token == ')':
        return reader.next()
    else:
        return read_form(reader)

def read_list(reader):
    assert reader.next() == '('

    form_list = []

    while True:
        form = read_list_form(reader)

        if form is None:
            raise SyntaxError("unexpected end of file")
        else:
            if form == ')':
                break
            form_list.append(form)

    return {'typ': 'lst', 'val': form_list}


#numbers
INTEGER_PATTERN = re.compile(r'([+-]?\d+)')
REAL_PATTERN = re.compile(r'[+-]?(\d)+[.](\d*)([eE]\d+)?')
RATIO_PATTERN = re.compile(r'[+-]?(\d+)/(\d+)')

#bools
BOOL_PATTERN = re.compile(r'#([fFtT])')

SYMBOL_PATTERN = re.compile(r'(\.\.\.|[+]|[-]|[a-zA-Z!$%&*/:<=>?~_^-][0-9a-zA-Z!$%&*/:<=>?~_^@.+-]*)') #taken from mit-scheme

STRING_PATTERN = re.compile(r'"((?:\\.|[^\\"])*)"') 
STRING_ESCAPE_PATTERN = re.compile(r'\\([\\rn])')

def read_atom(reader):
    t = reader.next()

    match = BOOL_PATTERN.fullmatch(t)
    if match:
        return {'typ': 'bool', 'val': "#"+match[1].lower()}

    match = INTEGER_PATTERN.fullmatch(t)
    if match:
        return {'typ': 'int', 'val': int(match[1])}

    match = SYMBOL_PATTERN.fullmatch(t)
    if match:
        return {'typ': 'sym', 'val': match[1]}

    match = STRING_PATTERN.fullmatch(t)
    if match:
        unescaped = re.sub(STRING_ESCAPE_PATTERN, match[1], '\1')
        return {'typ': 'str', 'val': match[1]}

    raise SyntaxError(f"unknown symbol {t}")

def test_read_atom_bool():
    b = read_atom(Reader(["#f"]))
    assert b == {'typ':'bool', 'val':'#f'}

def test_read_atom_int():
    r = Reader(["-345", "5000"])
    assert read_atom(r) == {'typ':'int', 'val':-345}
    assert read_atom(r) == {'typ':'int', 'val':5000}

    
def test_read_atom_symbol():
    r = Reader(["beep", "boop->beep"])
    assert read_atom(r) == {'typ':'sym', 'val':'beep'}
    assert read_atom(r) == {'typ':'sym', 'val':'boop->beep'}

