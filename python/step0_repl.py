#!/usr/bin/env python

import os
import sys
import readline

def _read(line):
    return line

def _eval(expr):
    return expr

def _print(val):
    return val

def rep(inp):
    _print(_eval(_read(inp)))

def main(args):
    try: 
        while True:
            inp = input("user> ")
            print(inp)
    except EOFError: 
        sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
