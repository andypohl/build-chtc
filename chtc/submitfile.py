"""Class for HTCondor submit files."""

import sys
import re
import os

_LINES = """\
universe = %s
%s
log = %s.log
output = %s.out
error = %s.err
transfer_output_files = %s.tar.gz
should_transfer_files = yes
when_to_transfer_output = on_exit
request_memory = %s
request_disk = %s
queue
"""

class SubmitFile(object):
    '''Simple class for an HTCondor submit file.'''

    def write(self):
        '''Write the submit file to disk.'''
        filename = self.prefix + '.submit'
        script_filename = self.prefix + '.sh'
        with open(filename, 'w') as fd:
            if self.interactive:
                variable_lines = "transfer_input_files = %s\n+IsBuildJob = true\nrequirements = (OpSysAndVer =?= \"SL6\") && (IsBuildSlot == true)" %(script_filename)
            else:
                variable_lines = "executable = " + script_filename
            lines = _LINES %(self.universe, variable_lines, self.prefix, self.prefix, self.prefix, self.prefix, self.memory, self.disk)
            fd.write(lines)

    def __init__(self, prefix):
        '''Just define some basics'''
        self.prefix = prefix
        self.universe = "Vanilla"
        self.disk = "5GB"
        self.memory = "1GB"
        self.interactive = False

##### Command-line testing (not in test suite)
def __run_tests():
    x = SubmitFile("mytest")
    x.interactive = True
    x.write()

if __name__ == '__main__':
    __run_tests()
