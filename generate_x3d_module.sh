
# saxon.Transform command line options:
# https://www.saxonica.com/documentation12/index.html#!using-xsl/commandline
# The jdk.xml.entityExpansionLimit=5000 parameter definition
# allows for parsing the X3D V4 dtd, which has a whole lot
# of XML ENTITY definitions

java -Djdk.xml.entityExpansionLimit=25000 \
     -Djdk.xml.totalEntitySizeLimit=200000 \
     -classpath ./SaxonHE12-9J/saxon-he-12.9.jar net.sf.saxon.Transform \
     -dtd:off \
     -s:./specifications/X3dUnifiedObjectModel-4.0.xml \
     -xsl:./x3d/stylesheets/X3duomToX3dPythonPackage.xslt \
     X3dPackageDirectory="build/x3d"
