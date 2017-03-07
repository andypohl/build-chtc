'''Tests for that dictionary class I found on on the internet.'''

#import unittest2 as unittest
import unittest
import sys
from chtc import SoftJson

class TestSoftJson(unittest.TestCase):
    '''Tests for SoftJson'''
    def setUp(self):
        self.empty = SoftJson()

    def test_good_json(self):
        # Remember to include *this* subdir in relative path because nose2
        # is executed from parent dir.
        self.empty.add_json_file("tests/data/good.json")
        pass

    def tearDown(self):
        del self.empty
