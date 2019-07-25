class Env:
    def __init__(self, outer=None, binds=[], exprs=[]):
        self.outer = outer
        self.data = {}

        try:
            vararg_idx = binds.index('&')
            if vararg_idx != len(binds) - 2:
                raise "Syntax error: invalid location for & operator"
            else:
                _binds = binds[:vararg_idx]
                _exprs = exprs[:vararg_idx]
                self.set(binds[-1], {'typ': 'lst', 'val': exprs[vararg_idx:]})

        except ValueError:
            _binds = binds[:]
            _exprs = exprs[:]

        for i, e in enumerate(_exprs):
            self.set(binds[i], e)

    def set(self, name, val):
        self.data[name] = val

    def find(self, name):
        if name in self.data:
            return self.data
        elif self.outer is not None:
            return self.outer.find(name)
        else: 
            return None

    def get(self, name):
        env_data = self.find(name)

        if env_data is not None:
            return env_data[name]
        else:
            raise Exception(f"{name} not found")

    def __repr__(self):
        return str(self.__dict__)


def test_env():
    env = Env()

    try:
        v = env.get('hi')
        assert False
    except: 
        pass

    env.set('hi', {'typ': 'int', 'val': 3})

    assert env.get('hi')['val'] == 3
