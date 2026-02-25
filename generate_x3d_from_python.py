import argparse
import subprocess
import tempfile

import os.path

import sys


import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# look for the x3d package in the local build directory
x3d_container = os.path.join( os.path.dirname(__file__),"build")

def test_x3d_package( container ):
    fp = os.path.join(container,"x3d/__init__.py")
    return os.path.isfile(fp)

if not test_x3d_package(x3d_container):
    message = f"container {x3d_container} does not contain x3d/__init__.py"
    logger.error(message)
    sys.exit(1)

sys.path.insert(0, x3d_container)

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
        sys.stderr.write(f"error writing XML encoding {str(exc)}\n")
        sys.exit(1)
        
logger.info("generate_x3d_from_python completed")
sys.exit(0)