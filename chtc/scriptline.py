"""Lines in a ShellScript"""
import re

class ScriptLine(object):
    """Just to keep track whether a line is a comment or not."""
    def __init__(self, string):
        self.line = string
        comm = re.compile(r'^\s*#')
        self.comment = comm.match(self.line) != None

    def is_comment(self):
        """Is this line a comment or not?"""
        return self.comment

    def __str__(self):
        return self.line
