'''Tests for that dictionary class I found on on the internet.'''

#import unittest2 as unittest
import unittest
import sys
from chtc import ShellScript

class TestShellScript(unittest.TestCase):
    '''Tests for ShellScript'''
    def setUp(self):
        self.script = ShellScript('test')

# Don't work in Python 2.6:
#    @unittest.skipIf(sys.version_info < (2,7))
#    def test_minimal(self):
#        '''Test the off-the-shelf ShellScript'''
#        self.assertGreater(len(self.script.lines), 0)
#        end_lines = END_LINES %(self.script.prefix)
#        self.assertMultiLineEqual(str(self.script), START_LINES + '\n' + end_lines)

    def test_adding(self):
        '''Test what happens when adding lines'''
        num_commands = self.script.num_commands()
        self.script.add_line("ls")
        num_commands = num_commands + 1
        self.assertEquals(num_commands, self.script.num_commands())
        self.script.add_line("# a comment")
        self.script.add_line("")
        self.assertEquals(num_commands, self.script.num_commands())
# Don't work in Python 2.6:
#        with self.assertRaises(TypeError):
#            self.script.add_line(52)

    def tearDown(self):
        del self.script
