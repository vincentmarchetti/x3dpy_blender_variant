"""
Script prepares a runs a suite of unittests based on 
performing a roundtrip of encodings XML --> Python --> XML

The roundtrip consists of 2 stages
stage 1: Starting with a valid XML encoding, generate the python code using the
X3dToPython XSLT stylesheet, enabled by the generate_python_encoding 

stage 2: Starting with a Python source code file (potentially but not necessarily 
as defined by stage 1 operation ); load the Python code, invoke the XML() function
on the model, and output to an x3d file. This procedure will be driven by the 
generate_python_from_x3d script.

This script will use as an input a list of filepaths to valid XML encoding files.

Stage 2 does require loading the x3d module, and which module is loaded will be
determined by the usual Python module resolution, including the PYTHONPATH env variable.
"""

import unittest
import os, os.path, sys, io
import subprocess
import shutil
import tempfile

import argparse

import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

parser=argparse.ArgumentParser(
    prog="generate_python_encoding"
)


parser.add_argument('-s','--samples')

args = parser.parse_args()

# put the local build of x3d package into sys.path
x3d_container = os.path.join(
    os.path.dirname(__file__),
    "../build"
)
sys.path.insert(0, x3d_container )

class RoundTripTest(unittest.TestCase):

    def __init__(self, filepath, stage ):
        """
        filepath a path to a valid XML encoding (.x3d)
        stage: integer value of 1 or 2
                the entered value is what will be tested
        """
        self.filepath = filepath
        self.stage = stage
        self.python_encoding = None
        self.temporary_directories = list()
        
        unittest.TestCase.__init__(self)
    
    @property
    def scripts_folder(self):
        """
        the location of the python wrapper scripts
        """
        return os.path.join(os.path.dirname(__file__),"..")
         
    def setUp(self):
        tempdir = tempfile.mkdtemp()
        pyBase = os.path.splitext( os.path.basename(self.filepath))[0] + ".py"
        self.python_encoding = os.path.join(tempdir, pyBase)
        self.temporary_directories.append(tempdir)
        logger.debug(f"python encoding: {self.python_encoding}")
        if (self.stage == 1):
            return
      
    def shortDescription(self):
        return f"stage {self.stage} file {os.path.basename(self.filepath)}"
        
    def tearDown(self ):
        for fd in self.temporary_directories:
            try:
                shutil.rmtree(fd)
            except Exception as exc:
                pass
        
    def runTest(self):
        testfunc = {
            1:self.execute_stage_1
        }[self.stage]
        code, error_message = testfunc()
        
        if code != 0:
            self.fail(error_message)
        return

    def execute_stage_1(self):
        """
        run the generate_python_encoding script is a separate process
        return a 2-tuple of returnCode, error_message
        error_message a string if returnCode != 0
        """
        generate_script_path = os.path.join(self.scripts_folder,"generate_python_encoding.py")
        
        commands = [
            'python',
            generate_script_path,
            '--outfile', self.python_encoding,
            self.filepath            
        ]
        with tempfile.TemporaryFile(mode="w+") as errp:
            res = subprocess.run(   commands,
                                    stdout= subprocess.DEVNULL,
                                    stderr= errp,
                                    text=True)
                                    
            if res.returncode != 0:
                errp.seek(0)
                return (res.returncode, errp.read() )
            
        # 2nd step is to validate that the python encoding file can be
        # 'executed' in python_encoding

        execute_script_path = os.path.join(self.scripts_folder,"execute_python_encoding.py")
        
        commands = [
            'python',
            execute_script_path,
            self.python_encoding          
        ]
        with tempfile.TemporaryFile(mode="w+") as errp:
            res = subprocess.run(   commands,
                                    stdout= subprocess.DEVNULL,
                                    stderr= errp,
                                    text=True)
                                    
            if res.returncode != 0:
                errp.seek(0)
                return (res.returncode, errp.read() )        
        return (0,None)

class TextTestResult(unittest.TextTestResult):
    def getDescription(self, test):
        return test.shortDescription()
    
    def printErrors(self):
        showErrors = False
        if showErrors:
            unittest.TextTestResult.printErrors(self)

class TextTestRunner(unittest.TextTestRunner):
    resultclass = TextTestResult


suite = unittest.TestSuite()
if args.samples:
    with open(args.samples,"r") as inp:
        for line in list(inp):  
            fpath = line.strip()         
            suite.addTest( RoundTripTest(fpath,1))
 
if __name__ == '__main__'  :
    TextTestRunner(verbosity=2).run(suite)
