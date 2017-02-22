"""Class to make shell (bash) scripts."""

import sys
from scriptline import ScriptLine

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
cd $BUILDDIR/src"""

# Scripts always end with these lines:
END_LINES = """\
# cleanup
cd ../
rm -rf src/

# tar it up
cd ../
tar cfz %s.tar.gz chtc
rm -rf software/"""

class ShellScript(object):
    """Describes a shell script, which can be written to a file."""
    def __init__(self, prefix):
        self.prefix = prefix
        self.lines = [ScriptLine(x) for x in START_LINES.split('\n')]
        self.insert_point = len(self.lines)
        self.lines.extend([ScriptLine(x) for x in END_LINES.split('\n')])
        self.lines[0].comment = False

    def add_line(self, line):
        """Add a new string to the list as a ScriptLine"""
        self.lines.insert(self.insert_point, ScriptLine(line))

    def write(self, comments=True):
        """Write this to a file called "prefix.sh"."""
        script_name = self.prefix + '.sh'
        try:
            with open(script_name, 'w') as script:
                for line in self.lines:
                    if (line.is_comment() and comments) or (not line.is_comment()):
                        script.write(str(line))
        except (IOError, OSError):
            sys.stderr.write("Trouble writing to %s" %(script_name))
            sys.exit(1)

    def __str__(self):
        return [str(x) for x in self.lines]

