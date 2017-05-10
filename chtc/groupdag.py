class GroupDag(object):        

    def __init__(self, software_array):
        '''A basic DAG data struct.  str() prints a DAG file'''
        self.software = software_array
        
    def __str__(self):
        '''Print out a DAG'''
        big_string = 'JOB prep noop.submit NOOP\n'
        for soft in self.software:
            prefix = soft.get_prefix()
            big_string += 'JOB ' + prefix + ' testing-' + prefix + '.submit\n'
        big_string += 'JOB collate noop.submit NOOP\n\n'
        for soft in self.software:
            prefix = soft.get_prefix()
            big_string += 'PARENT prep CHILD ' + prefix + '\n'
        big_string += 'PARENT '
        for soft in self.software:
            big_string += soft.get_prefix() + ' '
        big_string += 'CHILD collate\n'
        big_string += 'SCRIPT PRE prep ./prep.sh\n'
        big_string += 'SCRIPT POST collate ./collate.sh'
        return big_string

    def write(self, filename):
        '''Write a converted string out to the filename we've known in advance.'''
        with open(filename, 'w') as fd:
            fd.write(str(self) + '\n')
