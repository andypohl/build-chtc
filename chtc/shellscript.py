"""Class to make shell (bash) scripts."""

import sys
import re
import os

# Build scripts always have these lines:
BUILD_LINES = """\
#!/bin/bash

# Set up environment:
SOFTWAREDIR=$_CONDOR_SCRATCH_DIR/software
if [ -z $_CONDOR_SCRATCH_DIR ]; then 
    SOFTWAREDIR=$(pwd -P)/software
fi
export LD_LIBRARY_PATH=$SOFTWAREDIR/lib
export PATH=$SOFTWAREDIR/bin:$PATH

# Set up main build directory:
mkdir -p $SOFTWAREDIR/src

# cd into this directory to stage installs:
cd $SOFTWAREDIR/src

#### BUILDING PHASE

{{|BUILD_COMMANDS|}}
#### END OF BUILDING PHASE

# cleanup
cd ../
rm -rf src/

# tar it up
cd ../
tar cfz {{|PREFIX|}}.tar.gz software
rm -rf $SOFTWAREDIR"""

class ScriptLine(object):
    """Just to keep track whether a line is a comment or not."""
    def __init__(self, string, substitutions=None, should_exit=False):
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
        if self.comment==False and should_exit:
            self.line = self.line + ' || exit 1'
            
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
        lines = tmp
        return [ScriptLine(x, substitutions=None, should_exit=False) for x in lines.split('\n')]

    """Describes a shell script, which can be written to a file."""
    def __init__(self, prefix, substitutions=None, should_exit=False):
        self.prefix = prefix
        self.substitutions = substitutions
        self.should_exit = should_exit
        self.command_lines = []
        self.template_lines = self._add_template_lines(BUILD_LINES)
        self.template_lines[0].comment = False

    def num_commands(self):
        '''Inefficiently count the number of commands and return them.'''
        return sum([not x.is_comment() for x in self.catted()])

    def add_line(self, line, substitutions=None):
        """Add a new string to the list as a ScriptLine"""
        substs = self.substitutions
        if substitutions is not None:
            substs = substitutions
        self.command_lines.append(ScriptLine(line, substs, self.should_exit))

    def add_lines(self, lines, substitutions=None):
        """Add a list of commands to script."""
        for line in lines:
            self.add_line(line, substitutions)

    def write(self, comments=True, testing=False):
        """Write this to a file called "prefix.sh"."""
        script_name = self.prefix + '.sh'
        if testing:
            script_name = 'htcondor-tests/testing-' + script_name
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
        for tmp_line in template_lines:
            if str(tmp_line).strip() == "{{|BUILD_COMMANDS|}}":
                all_lines.extend(self.command_lines)
            else:
                all_lines.append(tmp_line)
        for line in all_lines:
            line.substitute("|PREFIX|", self.prefix)
            if comments or (not comments and not line.is_comment()):
                cleaned.append(line)
        return cleaned

    def __str__(self):
        return '\n'.join([str(x) for x in self.catted()])
