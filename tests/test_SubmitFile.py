'''A couple tests for SubmitFile class.'''

import unittest2 as unittest
#import unittest
import sys
from chtc import SubmitFile

class TestSubmitFile(unittest.TestCase):
    '''Tests for SubmitFile'''
    def setUp(self):
        # Don't initialize this with a regular python dict if you want to 
        # preserve ordering!
        self.sub = SubmitFile("mysoft")

    def test_queue_is_last(self):
        '''Make sure queue line is last.'''
        keys = self.sub.keys()
        self.assertEqual(keys[-1], "queue")

    def test_locked(self):
        '''Make sure we can't add lines.'''
        self.assertRaises(KeyError, self.sub.__setitem__, 'newline', 'newvalue')

    def test_can_change_specific_lines(self):
        '''We can change lines though.'''
        self.assertEquals(self.sub['request_memory'], '500MB')
        self.sub['request_memory'] = '4GB'
        self.assertEquals(self.sub['request_memory'], '4GB')

    def tearDown(self):
        del self.sub