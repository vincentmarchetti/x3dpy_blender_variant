

import os,os.path,sys,subprocess
import logging
import re
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# saxon.Transform command line options:
# https://www.saxonica.com/documentation12/index.html#!using-xsl/commandline
# The jdk.xml.entityExpansionLimit=5000 parameter definition
# allows for parsing the X3D V4 dtd, which has a whole lot
# of XML ENTITY definitions

# preconditions:
# through CLASSPATH or other methd the Java class net.sf.Saxon is resolvable
# This has been tested getting net.sf.saxon.Transform from SaxonHE12-9J/saxon-he-12.9.jar"
# obtained from https://github.com/Saxonica/Saxon-HE/releases ; Feb 2026

# the stylesheet ./x3d/stylesheets/X3duomToX3dPythonPackage.xslt
# expects to locate ./x3d/tooltips/x3d-4.0.profile.xml
# and dtd file      ./x3d/tooltips/profile.dtd

SCRIPT_DIR=os.path.dirname(__file__)
PACKAGE_DIR =os.path.join(SCRIPT_DIR,"build/x3d")

command = [
    "java",
    "-Djdk.xml.entityExpansionLimit=%i" % (25000,),
    "-Djdk.xml.totalEntitySizeLimit=%i" % (200000,),
    "net.sf.saxon.Transform",
    "-dtd:off",
    "-s:%s/specifications/X3dUnifiedObjectModel-4.0.xml" % SCRIPT_DIR,
    "-xsl:%s/x3d/stylesheets/X3duomToX3dPythonPackage.xslt" % SCRIPT_DIR,
    "X3dPackageDirectory=%s" % PACKAGE_DIR
]
logger.debug("command: %s" % " ".join(command))
res = subprocess.run(command)

if res.returncode != 0:
    logger.error("XSLT failed with result code %i" % res.returncode)
    sys.exit(res.returncode)
    
logger.debug("XSLT completed")

# now apply a change to the message printed
MODULE_PATH=os.path.join(PACKAGE_DIR,"x3d.py")

with open(MODULE_PATH,"r") as inp:
    module_lines = inp.readlines()
    
logger.debug("read %i module lines" % len(module_lines))

try:
    os.remove( MODULE_PATH )
except Exception as exc:
    logger.error("Failed as removing original %s" % MODULE_PATH)
    sys.exit(1)
    

replace_pattern=re.compile(r"x3d.py package\s+(.*)\s+loaded, have fun with X3D Graphics!")
replacement_text = r"x3d.py package \1 modified by x3dpy_containerfield loaded, have fun with X3D Graphics!"

try:
    with open(MODULE_PATH,"w") as outp:
        for line in module_lines:
            #outp.write( replace_pattern.sub(replacement_text ))
            outp.write( replace_pattern.sub( replacement_text, line ))
except Exception as exc:
    logger.error("replacement failed: %s" % str(exc))
    sys.exit(1)

logger.info("x3d package generation completed")
sys.exit(0)



