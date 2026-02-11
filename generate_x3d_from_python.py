import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

import sys


INFILE="/Users/vmarchetti/Documents/SPRI/x3d_package_fix/build/simplified_hanim.py"
OUTFILE="/Users/vmarchetti/Documents/SPRI/x3d_package_fix/build/simplified_hanim.x3d"

with open(INFILE,"r") as inp:
    try:
        exec(inp.read())
    except Exception as exc:
        logger.exception("error executing python encoding")
        sys.exit(1)
    
try:
    newModel
except Exception as exc:
    logger.exception("error referencing newModel")
    sys.exit(1)
    


with open(OUTFILE,"w") as outp:
    try:
        outp.write( newModel.XML() )
    except Exception as exc:
        logger.exception("error writing XML encoding")
        sys.exit(1)
        
logger.debug(f"encoding written to {OUTFILE}")