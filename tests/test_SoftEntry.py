'''SoftEntry tests.  Not using test data files.'''

import unittest2 as unittest
#import unittest
import sys
from datetime import date
from chtc import SoftEntry
from chtc import CaseInsensitiveDict

class TestSoftEntry(unittest.TestCase):
    '''Tests for SoftEntry'''
    def setUp(self):
        cid = CaseInsensitiveDict({'Software': 'MySoft', 'Version': '1.0', 'URL': 'http://example.com/MySoft-1.0.tar.gz'})
        self.soft1 = SoftEntry(cid)
        # with a release date
        cid = CaseInsensitiveDict({'Software': 'MySoft', 'Version': '1.0', 'URL': 'http://example.com/MySoft-1.0.tar.gz', 'Release_Date': '2012-04-15'})
        self.soft2 = SoftEntry(cid)

    def test_empty_init(self):
        self.assertRaises(TypeError, SoftEntry.__init__, None)

    def test_prefix(self):
        expected_prefix = 'MySoft-1.0'
        self.assertEquals(self.soft1.get_prefix(), expected_prefix)
        self.assertEquals(self.soft2.get_prefix(), expected_prefix)

    def test_release_date(self):
        self.assertIsNone(self.soft1.get_release_date())
        dt = self.soft2.get_release_date()
        self.assertIsNotNone(dt)
        self.assertIsInstance(dt, date)
        self.assertEquals(dt.year, 2012)
        self.assertEquals(dt.month, 4)
        self.assertEquals(dt.day, 15)

    def tearDown(self):
        del self.soft1
        del self.soft2
