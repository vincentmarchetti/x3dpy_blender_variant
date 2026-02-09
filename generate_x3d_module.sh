
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

java -Djdk.xml.entityExpansionLimit=25000 \
     -Djdk.xml.totalEntitySizeLimit=200000 \
     net.sf.saxon.Transform \
     -dtd:off \
     -s:./specifications/X3dUnifiedObjectModel-4.0.xml \
     -xsl:./x3d/stylesheets/X3duomToX3dPythonPackage.xslt \
     X3dPackageDirectory="build/x3d"
