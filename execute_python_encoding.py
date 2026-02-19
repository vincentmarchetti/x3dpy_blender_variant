
import os, os.path, sys, subprocess

import argparse

parser=argparse.ArgumentParser(
    prog="execute_python_encoding"
)

parser.add_argument('infile')

args = parser.parse_args()

try:
    with open(args.infile,"r") as inp:
        exec(inp.read())
except Exception as exc:
    sys.stderr.write(str(exc))
    sys.exit(1)
sys.exit(0)