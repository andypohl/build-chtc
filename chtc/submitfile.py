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
        self.tarball = prefix + '.$(linux).tar.gz'
        self['universe'] = 'vanilla'
        self['grid_resource'] = None
        self['remote_universe'] = None
        self['executable'] = self.script_name
        self['arguments'] = '$(linux)'
        self['log'] = prefix + '.$(linux).log'
        self['error'] = prefix + '.$(linux).err'
        self['output'] = prefix + '.$(linux).out'
        self['transfer_input_files'] = None
        self['transfer_output_files'] = [self.tarball]
        self['should_transfer_files'] = 'yes'
        self['when_to_transfer_output'] = 'on_exit'
        self['requirements'] = '((OpSysMajorVer == $(linux)) && (IsBuildSlot == True))'
        self['+IsBuildJob'] = 'True'
        self['request_disk'] = '5GB'
        self['request_memory'] = '2GB'
        self['queue'] = 'queue linux in (6,7)'
        self._locked = True
        self.testing = False

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
                if key == 'queue' and len(value) > 0:
                    line = value
                elif len(value) > 0:
                    line = line + ' = ' + value
                bigstring = bigstring + line + '\n'
        return bigstring.rstrip() + '\n'

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
    # Slightly different than the regular SubmitFile class
    def __init__(self, prefix):
        SubmitFile.__init__(self, prefix)
        self['executable'] = None
        self['+IsBuildJob'] = 'true'
        self['requirements'] = ['(OpSysAndVer =?= \"SL6\")', '(IsBuildSlot == true)']
        self['transfer_input_files'] = [self.script_name]

# Could also have a BOSCO-style submit file too.
class BoscoSubmitFile(SubmitFile):
    # Bosco flavor
    def __init__(self, prefix, ssh_submit):
        SubmitFile.__init__(self, prefix)
        self['universe'] = "grid"
        self['remote_universe'] = "vanilla"
        self['grid_resource'] = "batch condor " + ssh_submit

class TestingSubmitFile(SubmitFile):
    # with the wrapper
    def __init__(self, prefix):
        SubmitFile.__init__(self, prefix)
        self.script_name = 'testing-' + prefix + '.sh'
        verdict_file = 'testing-' + prefix + '.verdict.txt'
        self['executable'] = 'wrapper-testing.sh'
        self['arguments'] = self.script_name + ' ' + verdict_file
        self['log'] = 'testing-' + prefix + '.log'
        self['error'] = 'testing-' + prefix + '.err'
        self['output'] = 'testing-' + prefix + '.out'
        self['transfer_input_files'] = [self.script_name]
        self['transfer_output_files'] = [verdict_file]
        self.filename = 'htcondor-tests/testing-' + self.filename
        self.testing = True

##### Command-line testing (not in test suite)
def __run_tests():
    x = SubmitFile("mytest")
    x['transfer_output_files'] = [x.tarball, x.example_tarball]
    print(x)

if __name__ == '__main__':
    __run_tests()
