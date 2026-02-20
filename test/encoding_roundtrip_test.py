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
logger.setLevel(logging.WARN)

parser=argparse.ArgumentParser(
    prog="generate_python_encoding"
)


parser.add_argument('-s','--samples' ,help='text file of .x3d files, 1 filepath per line')
parser.add_argument('--omit-errorlist', action='store_true', 
                    dest="omit_errorlist",
                    help='suppress printing of error details')

# Developer Note: the python-path argument can be used to resolve to a x3d.py that is not the local build
parser.add_argument('-p', '--python-path', 
                    dest="python_path",
                    help='addition to search path to locate x3d module')

args = parser.parse_args()
    
if args.python_path:
    x3d_container = args.python_path
else:
    # use the local build of x3d package
    x3d_container = os.path.join(
                        os.path.dirname(__file__),
                        "../build"
                    )
# to avoid getting fooled by Python finding another x3d package somewhere
# we require that x3d_container has a x3d folder with an x3d/__init__.py file
# following function returns True if such an x3d/__init__.py is found
def test_x3d_package( container ):
    fp = os.path.join(container,"x3d/__init__.py")
    return os.path.isfile(fp)

if not test_x3d_package(x3d_container):
    message = f"container {x3d_container} does not contain x3d/__init__.py"
    raise ValueError(message)

logger.info(f"x3d_container: {x3d_container}")


class RoundTripTest(unittest.TestCase):

    # add the x3d_container value from module scope as a class member
    python_path = x3d_container

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
    def test_environ(self):
        # returns the a mapping with the current environment values
        # modified by defining PYTHONPATH
        retVal = dict( os.environ )
        retVal["PYTHONPATH"] = self.python_path
        return retVal
        
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
        
        x3dBase = os.path.basename(self.filepath)
        self.x3d_encoding = os.path.join(tempdir, x3dBase)
        
        self.temporary_directories.append(tempdir)
        logger.debug(f"python encoding: {self.python_encoding}")
        if (self.stage == 1):
            return
        else:
            code, errp = self.execute_stage_1()
            logger.info("setUp: %s" % ((code, errp),))
            if (code != 0):
                self.skipTest("no python encoding")
            return
      
    def shortDescription(self):
        prefix = {
            1:"xml -> python",
            2:"python -> xml",
        }
        file_root, _ = os.path.splitext( os.path.basename(self.filepath))
        return f"{prefix[self.stage]} for {file_root}"
        
    def tearDown(self ):
        for fd in self.temporary_directories:
            try:
                shutil.rmtree(fd)
            except Exception as exc:
                pass
        
    def runTest(self):
        testfunc = {
            1:self.execute_stage_1,
            2:self.execute_stage_2
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
                                    env=self.test_environ,
                                    stderr= errp,
                                    text=True)
                                    
            if res.returncode != 0:
                errp.seek(0)
                return (res.returncode, errp.read() )        
        return (0,None)

    def execute_stage_2(self):
        """
        run the generate_python_encoding script is a separate process
        return a 2-tuple of returnCode, error_message
        error_message a string if returnCode != 0
        """
        generate_script_path = os.path.join(self.scripts_folder,"generate_x3d_from_python.py")
        
        commands = [
            'python',
            generate_script_path,
            '--outfile', self.x3d_encoding,
            self.python_encoding            
        ]
        with tempfile.TemporaryFile(mode="w+") as errp:
            res = subprocess.run(   commands,
                                    env=self.test_environ,
                                    stdout= subprocess.DEVNULL,
                                    stderr= errp,
                                    text=True)
                                    
            if res.returncode != 0:
                errp.seek(0)
                return (res.returncode, errp.read() )
        return (0,None)

class TextTestResult(unittest.TextTestResult):

    # set a class member based on the module level args option
    show_errors = not args.omit_errorlist

    def getDescription(self, test):
        return test.shortDescription()
    
    
    def printErrors(self):
        # this is an override of unittest.TextTestResult.printErrord
        # that always shows errors.

        if self.show_errors:
            unittest.TextTestResult.printErrors(self)

class TextTestRunner(unittest.TextTestRunner):
    resultclass = TextTestResult


suite = unittest.TestSuite()
if args.samples:
    with open(args.samples,"r") as inp:
        for line in list(inp):  
            fpath = line.strip() 
            suite.addTest( RoundTripTest(fpath,1))        
            suite.addTest( RoundTripTest(fpath,2))
 
if __name__ == '__main__'  :
    TextTestRunner(verbosity=2).run(suite)
