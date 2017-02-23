'''Tests for that dictionary class I found on on the internet.'''

import unittest
from chtc import ShellScript
from chtc.shellscript import START_LINES, END_LINES

class TestShellScript(unittest.TestCase):
    '''Tests for ShellScript'''
    def setUp(self):
        self.script = ShellScript('test')

    def test_minimal(self):
        '''Test the off-the-shelf ShellScript'''
        self.assertGreater(len(self.script.lines), 0)
        self.assertMultiLineEqual(str(self.script), START_LINES + '\n' + END_LINES)

    def test_adding(self):
        '''Test what happens when adding lines'''
        num_commands = self.script.num_commands()
        self.script.add_line("ls")
        num_commands = num_commands + 1
        self.assertEquals(num_commands, self.script.num_commands())
        self.script.add_line("# a comment")
        self.script.add_line("")
        self.assertEquals(num_commands, self.script.num_commands())
        with self.assertRaises(TypeError):
            self.script.add_line(52)

    def tearDown(self):
        del self.script
