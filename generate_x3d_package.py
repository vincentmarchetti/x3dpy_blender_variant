

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
