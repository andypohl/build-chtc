"""Class for HTCondor submit files."""

from ordereddict import OrderedDict

# The base class is mostly an OrderedDict, which means we can iterate over the iterkeys
# when printing it out in the order we put those keys in.  So all the keys are established
# in the constructor because in a submit file, the "queue" line must be at the end.

class SubmitFile(OrderedDict):
    '''Simple class for an HTCondor submit file.'''

    def __init__(self, prefix):
        '''Just define some basics'''
        OrderedDict.__init__(self)
        self._locked = False
        self.prefix = prefix
        self.script_name = prefix + '.sh'
        self.filename = prefix + '.submit'
        self.tarball = prefix + '.tar.gz'
        self.example_tarball = 'examples-' + prefix + '.tar.gz'
        self['universe'] = 'vanilla'
        self['executable'] = self.script_name
        self['log'] = prefix + '.log'
        self['error'] = prefix + '.err'
        self['output'] = prefix + '.out'
        self['transfer_input_files'] = None
        self['transfer_output_files'] = [self.example_tarball]
        self['should_transfer_files'] = 'yes'
        self['when_to_transfer_output'] = 'on_exit'
        self['requirements'] = None
        self['+IsBuildJob'] = None
        self['request_disk'] = '5GB'
        self['request_memory'] = '1GB'
        self['queue'] = ''
        self._locked = True

    def __str__(self):
        '''Convert to string.'''
        bigstring = ''
        for key in self.iterkeys():
            value = self[key]
            if value is not None:
                line = key
                if isinstance(value, list):
                    joiner = ' && ' if key == 'requirements' else ', '
                    value = joiner.join(value)
                if len(value) > 0:
                    line = line + ' = ' + value
                bigstring = bigstring + line + '\n'
        return bigstring.rstrip()

    def __setitem__(self, key, value):
        '''Don't allow additional lines to the submit file.'''
        if self._locked and key not in self:
            raise KeyError("Add to submit file specification by extending class.")
        OrderedDict.__setitem__(self, key, value)

    def write(self):
        '''Write a converted string out to the filename we've known in advance.'''
        with open(self.filename, 'w') as fd:
            fd.write(str(self))

# Inherited class 
class InteractiveSubmitFile(SubmitFile):
    # Slightly different than the 
    def __init__(self, prefix):
        SubmitFile.__init__(self, prefix)
        self['executable'] = None
        self['+IsBuildJob'] = 'true'
        self['requirements'] = ['(OpSysAndVer =?= \"SL6\")', '(IsBuildSlot == true)']
        self['transfer_input_files'] = [self.script_name]

# Could also have a BOSCO-style submit file too.

##### Command-line testing (not in test suite)
def __run_tests():
    x = SubmitFile("mytest")
    x['transfer_output_files'] = [x.tarball, x.example_tarball]
    print(x)

if __name__ == '__main__':
    __run_tests()
