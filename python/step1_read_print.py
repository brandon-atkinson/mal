#!/usr/bin/env python

import os
import sys
import readline
import reader
import printer

def _read(line):
    return reader.read_str(line)

def _eval(expr):
    return expr

def _print(val):
    return printer.pr_str(val, True)

def rep(inp):
    return _print(_eval(_read(inp)))

def main(args):
    try: 
        while True:
            try: 
                inp = input("user> ")
                print(rep(inp))
            except SyntaxError:
                print("end of input")
    except EOFError: 
        sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
