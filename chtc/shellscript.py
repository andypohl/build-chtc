"""Class to make shell (bash) scripts."""

import sys
import re
import os

# Scripts always start with these lines:
START_LINES = """\
#!/bin/bash

# Set up environment:
BUILDDIR=$_CONDOR_SCRATCH_DIR/software
export LD_LIBRARY_PATH=$BUILDDIR/lib
export PATH=$BUILDDIR/bin:$PATH

# Set up main build directory:
mkdir -p $BUILDDIR/src

# cd into this directory to stage installs:
cd $BUILDDIR/src\n"""

# Scripts always end with these lines:
END_LINES = """\
# cleanup
cd ../
rm -rf src/

# tar it up
cd ../
tar cfz %s.tar.gz chtc
rm -rf software/"""

class ScriptLine(object):
    """Just to keep track whether a line is a comment or not."""
    def __init__(self, string):
        if not isinstance(string, str) and not isinstance(string, unicode):
            raise TypeError("commands must be strings")
        self.line = string
        comm = re.compile(r'^\s*(#|$)')
        self.comment = comm.match(self.line) != None

    def is_comment(self):
        """Is this line a comment or not?"""
        return self.comment

    def __str__(self):
        return self.line

class ShellScript(object):
    """Describes a shell script, which can be written to a file."""
    def __init__(self, prefix):
        self.prefix = prefix
        self.lines = [ScriptLine(x) for x in START_LINES.split('\n')]
        self.insert_point = len(self.lines)
        end_lines = END_LINES %(self.prefix)
        self.lines.extend([ScriptLine(x) for x in end_lines.split('\n')])
        self.lines[0].comment = False

    def num_commands(self):
        '''Count the number of commands and return them.'''
        return sum([not x.is_comment() for x in self.lines])

    def add_line(self, line):
        """Add a new string to the list as a ScriptLine"""
        self.lines.insert(self.insert_point, ScriptLine(line))

    def add_lines(self, lines):
        """Add a list of commands to script."""
        for line in lines:
            self.add_line(line)

    def write(self, comments=True):
        """Write this to a file called "prefix.sh"."""
        script_name = self.prefix + '.sh'
        try:
            with open(script_name, 'w') as script_fd:
                for line in self.lines:
                    if (line.is_comment() and comments) or (not line.is_comment()):
                        script_fd.write(str(line) + '\n')
        except (IOError, OSError):
            # kick the exception up the line, though I'm not sure how to test for this
            raise OSError("ERROR: trouble writing to %s" %(script_name))
        else:
            os.chmod(script_name, 0755)

    def __str__(self):
        return '\n'.join([str(x) for x in self.lines])
