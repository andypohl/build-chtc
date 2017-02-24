"""Class to make shell (bash) scripts."""

import sys
import re
import os

# Scripts always start with these lines:
LINES = """\
#!/bin/bash

# Set up environment:
BUILDDIR=$_CONDOR_SCRATCH_DIR/software
export LD_LIBRARY_PATH=$BUILDDIR/lib
export PATH=$BUILDDIR/bin:$PATH

# Set up main build directory:
mkdir -p $BUILDDIR/src

# cd into this directory to stage installs:
cd $BUILDDIR/src

#### BUILDING PHASE

{{|BUILD_COMMANDS|}}

#### END OF BUILDING PHASE

# cleanup
cd ../
rm -rf src/

# tar it up
cd ../
tar cfz %s.tar.gz software
rm -rf $BUILDDIR
"""
EXAMPLE_LINES = """\
#### EXAMPLES PACKAGING

export EXAMPLEDIR=$_CONDOR_SCRATCH_DIR/examples
mkdir -p $EXAMPLEDIR
cd $_CONDOR_SCRATCH_DIR

{{|EXAMPLE_COMMANDS|}}

cd $_CONDOR_SCRATCH_DIR
tar cfz examples-%s.tar.gz $EXAMPLEDIR
rm -rf $EXAMPLEDIR

#### ALL DONE
"""

class ScriptLine(object):
    """Just to keep track whether a line is a comment or not."""
    def __init__(self, string, substitutions=None):
        if not isinstance(string, str) and not isinstance(string, unicode):
            raise TypeError("commands must be strings")
        self.line = string
        comm = re.compile(r'^\s*(#|$)')
        self.comment = comm.match(self.line) != None
        if self.comment==False and substitutions is not None:
            if not isinstance(substitutions, list):
                raise TypeError("Expecting substitutions to be a list.")
            for subst in substitutions:
                if not isinstance(subst, tuple):
                    raise TypeError("Expecting substitutions to be a list of before/after tuples.")
                self.substitute(subst[0], subst[1])
            
    def substitute(self, before, after):
        '''Try to substitute in mustache style e.g. before="TIMESTAMP", after="2016-03-04"'''
        mustached = "{{" + before + "}}"
        self.line = self.line.replace(mustached, after)

    def is_comment(self):
        """Is this line a comment or not?"""
        return self.comment

    def __str__(self):
        return self.line

class ShellScript(object):

    def _add_template_lines(self, tmp):
        '''Process templates'''
        lines = tmp %(self.prefix)
        return [ScriptLine(x) for x in lines.split('\n')]

    """Describes a shell script, which can be written to a file."""
    def __init__(self, prefix, substitutions=None):
        self.prefix = prefix
        self.substitutions = substitutions
        self.template_lines = self._add_template_lines(LINES)
        self.example_template_lines = self._add_template_lines(EXAMPLE_LINES)
        self.command_lines = []
        self.example_lines = []
        self.template_lines[0].comment = False

    def num_commands(self):
        '''Inefficiently count the number of commands and return them.'''
        return sum([not x.is_comment() for x in self.catted()])

    def add_line(self, line, substitutions=None, is_example=False):
        """Add a new string to the list as a ScriptLine"""
        substs = self.substitutions
        if substitutions is not None:
            substs = substitutions
        # I don't like this.  There must be some way to abstract this better.
        if is_example:
            self.example_lines.append(ScriptLine(line, substs))
        else:
            self.command_lines.append(ScriptLine(line, substs))

    def add_lines(self, lines, substitutions=None, is_examples=False):
        """Add a list of commands to script."""
        for line in lines:
            self.add_line(line, substitutions, is_examples)

    def write(self, comments=True):
        """Write this to a file called "prefix.sh"."""
        script_name = self.prefix + '.sh'
        try:
            with open(script_name, 'w') as script_fd:
                for line in self.catted(comments):
                    script_fd.write(str(line) + '\n')
        except (IOError, OSError):
            # kick the exception up the line, though I'm not sure how to test for this
            raise OSError("ERROR: trouble writing to %s" %(script_name))
        else:
            os.chmod(script_name, 0755)

    # A list of all the lines together
    def catted(self, comments=True):
        '''A list of all the lists of lines combined.'''
        all_lines = []
        cleaned = []
        template_lines = self.template_lines
        if len(self.example_lines) > 0:
            template_lines.extend(self.example_template_lines)
        for tmp_line in template_lines:
            if str(tmp_line).strip() == "{{|BUILD_COMMANDS|}}":
                all_lines.extend(self.command_lines)
            elif str(tmp_line).strip() == "{{|EXAMPLE_COMMANDS|}}":
                all_lines.extend(self.example_lines)
            else:
                all_lines.append(tmp_line)
        if comments==False:
            for line in all_lines:
                if not line.is_comment():
                    cleaned.append(line)
        else:
            cleaned = all_lines
        return cleaned

    def __str__(self):
        return '\n'.join([str(x) for x in self.catted()])
