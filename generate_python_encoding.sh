
# saxon.Transform command line options:
# https://www.saxonica.com/documentation12/index.html#!using-xsl/commandline
# The jdk.xml.entityExpansionLimit=5000 parameter definition
# allows for parsing the X3D V4 dtd, which has a whole lot
# of XML ENTITY definitions

# using a TEMPFILE because I don't know how to stream the generead python
# text into the sed invocation that follows
TEMPFILE=temp.deleteme
MODEL_BASENAME=simplified_hanim
java -Djdk.xml.entityExpansionLimit=5000 \
     net.sf.saxon.Transform \
     -dtd:off \
     -s:../original/$MODEL_BASENAME.x3d \
     -xsl:./x3d/stylesheets/X3dToPython.xslt \
     -o:$TEMPFILE  && \
# following sed operation will strip the diagnostic tests from the python code     
sed -e '/Self-test diagnostics/q' $TEMPFILE > build/$MODEL_BASENAME.py && \
rm $TEMPFILE
