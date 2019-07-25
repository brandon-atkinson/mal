#!/usr/bin/env python

import os
import sys
import readline
import reader
import printer
import env
import core
import traceback

def _read(line):
    return reader.read_str(line)

def _eval(ast):
    return core.eval(ast)

def _print(val):
    return printer.pr_str(val, True)

def rep(inp):
    return _print(_eval(_read(inp)))

rep('(def! load-file (fn* (f) (eval (read-string (str "(do " (slurp f) ")")))))')

def main(args):
    try: 
        while True:
            try: 
                inp = input("user> ")
                print(rep(inp))
            except Exception as se:
                print("Error: " + str(se))
                traceback.print_exc()
    except EOFError: 
        sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
