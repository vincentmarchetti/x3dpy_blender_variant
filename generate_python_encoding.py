
import argparse
import subprocess
import tempfile

import os.path

import sys
import logging
logger = logging.getLogger()
logger.addHandler(
    logging.StreamHandler(sys.stdout)
);
logger.setLevel(logging.DEBUG)

here = os.path.dirname(__file__)

parser=argparse.ArgumentParser(
    prog="generate_python_encoding"
)

parser.add_argument('infile')
parser.add_argument('-o','--outfile')

args = parser.parse_args()

def run():
    with tempfile.TemporaryDirectory() as tempdir:
        tempfilename = os.path.join(tempdir, "pythonenc.py")
        commands = [
            'java',
            ('-Djdk.xml.entityExpansionLimit=%i' % 5000),
            'net.sf.saxon.Transform',
            '-dtd:off',
            ('-s:%s' % args.infile),
            ('-xsl:%s' % os.path.join(here, './x3d/stylesheets/X3dToPython.xslt')),
            ('-o:%s' % tempfilename)
        ]
        logger.debug(f"commands: {' '.join(commands)}")
    
        res = subprocess.run(   commands ,
                                text=True) # text = True will allow capture of stderr
        logger.info(f"java call returned with code {res.returncode}")
        if (res.returncode != 0):
            sys.stdout.write("XLT error: %s" % res.stderr )
            sys.exit(1)
            
        # post processing
        if args.outfile:
            outp = open(args.outfile,'w')
        else:
            outp = os.devnull
        with open(tempfilename,"r") as inp, outp:
            for fline in sed_lines(inp):
                outp.write(fline)
                
        logger.info("completed")
        sys.exit(0)

# re and sed_line generator intended to remove the
# self diagnostic tests that the standard XSLT sheet adds
# to generated Python code

import re 
BREAK_PATTERN = re.compile(r"Self-test\s+diagnostics")

def sed_lines(inp):
    for fline in inp:
        if BREAK_PATTERN.search(fline):
            return
        else:
            yield fline
run()
        

