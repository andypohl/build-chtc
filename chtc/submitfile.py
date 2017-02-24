"""Class for HTCondor submit files."""

import sys
import re
import os
from ordereddict import OrderedDict

# The base class is mostly an OrderedDict, which means we can iterate over the iterkeys
# when printing it out in the order we put those keys in.  So all the keys are established
# in the constructor because in a submit file, the "queue" line must be at the end.
# Although thinking about it, maybe queue should be outside the dict.

class SubmitFile(object):
    '''Simple class for an HTCondor submit file.'''

    def __init__(self, prefix):
        '''Just define some basics'''
        self.lines = OrderedDict()
        self.prefix = prefix
        self.script_name = prefix + '.sh'
        self.filename = prefix + '.submit'
        self.tarball = prefix + '.tar.gz'
        self.example_tarball = 'examples-' + prefix + '.tar.gz'
        self.lines['universe'] = 'vanilla'
        self.lines['executable'] = self.script_name
        self.lines['log'] = prefix + '.log'
        self.lines['error'] = prefix + '.err'
        self.lines['output'] = prefix + '.out'
        self.lines['transfer_input_files'] = None
        self.lines['transfer_output_files'] = None
        self.lines['should_transfer_files'] = 'yes'
        self.lines['when_to_transfer_output'] = 'on_exit'
        self.lines['requirements'] = None
        self.lines['+IsBuildJob'] = None
        self.lines['request_disk'] = '5GB'
        self.lines['request_memory'] = '1GB'
        self.lines['queue'] = ''
        self.set_inputs([])
        self.set_outputs([self.tarball])

    def set_outputs(self, array):
        self.lines['transfer_output_files'] = None
        self.output_list = array
        if len(array) > 0:
            self.lines['transfer_output_files'] = ', '.join(array)

    def get_outputs(self):
        return self.output_list

    def set_inputs(self, array):
        self.lines['transfer_input_files'] = None
        self.input_list = array
        if len(array) > 0:
            self.lines['transfer_input_files'] = ', '.join(array)

    def get_inputs(self):
        return self.input_list

    def __str__(self):
        bigstring = ''
        for key in self.lines.iterkeys():
            value = self.lines[key]
            if value is not None:
                line = key 
                if len(value) > 0:
                    line = line + ' = ' + value
                bigstring = bigstring + line + '\n'
        return bigstring.rstrip()

    def write(self):
        with open(self.filename, 'w') as fd:
            fd.write(str(self))

# Inherited class 
class InteractiveSubmitFile(SubmitFile):
    # Slightly different than the 
    def __init__(self, prefix):
        SubmitFile.__init__(self, prefix)
        self.lines['executable'] = None
        self.lines['+IsBuildJob'] = 'true'
        self.lines['requirements'] = '(OpSysAndVer =?= \"SL6\") && (IsBuildSlot == true)'
        self.set_inputs([self.script_name])

# Could also have a BOSCO-style submit file too.

##### Command-line testing (not in test suite)
def __run_tests():
    x = InteractiveSubmitFile("mytest")
    x.set_outputs([x.tarball, x.example_tarball])
    print(x)

if __name__ == '__main__':
    __run_tests()
