import argparse
import subprocess
import tempfile

import os.path

import sys


import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

here = os.path.dirname(__file__)

parser=argparse.ArgumentParser(
    prog="generate_x3d_from_python"
)

parser.add_argument('infile')
parser.add_argument('-o','--outfile')

args = parser.parse_args()

with open(args.infile,"r") as inp:
    try:
        exec(inp.read())
    except Exception as exc:
        sys.stderr.write(f"error executing python encoding {str(exc)}\n")
        sys.exit(1)
    
try:
    newModel
except Exception as exc:
    sys.stderr.write(f"error referencing newModel {exc}\n")
    sys.exit(1)


if args.outfile:
    outp = open(args.outfile,"w")
else:
    outp = sys.devnull
    
with outp:
    try:
        outp.write( newModel.XML() )
    except Exception as exc:
        sys.stderr.write(f"error writing XML encoding {exc.message()}\n")
        sys.exit(1)
        
logger.info("generate_x3d_from_python completed")
sys.exit(0)