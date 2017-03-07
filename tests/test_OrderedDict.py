'''Tests for that OrderedDict Python 2.6 backport I found on on the internet.'''

import unittest2 as unittest
#import unittest
import sys
from chtc import OrderedDict

class TestOrderedDict(unittest.TestCase):
    '''Tests for OrderedDict'''
    def setUp(self):
        # Don't initialize this with a regular python dict if you want to 
        # preserve ordering!
        self.dict1 = OrderedDict()
        self.dict1['A'] = 4
        self.dict1['B'] = 3
        self.dict1['C'] = 2
        self.dict2 = OrderedDict()
        self.dict2['A'] = 4
        self.dict2['B'] = 3
        self.dict2['C'] = 2
        self.dict3 = OrderedDict()
        self.dict3['A'] = 4
        self.dict3['C'] = 2
        self.dict3['B'] = 3

    def test_equal(self):
        '''We don't expect different dicts with same keys but in different orders to be equal'''
        self.assertEqual(self.dict1, self.dict2)
        self.assertNotEqual(self.dict1, self.dict3)

    def test_iteration(self):
        '''Should iterate keys as A, B, C then A, C, B'''
        it = self.dict1.iterkeys()
        key = it.next()
        self.assertEqual(key, 'A')
        key = it.next()
        self.assertEqual(key, 'B')
        key = it.next()
        self.assertEqual(key, 'C')
        it = self.dict3.iterkeys()
        key = it.next()
        self.assertEqual(key, 'A')
        key = it.next()
        self.assertEqual(key, 'C')
        key = it.next()
        self.assertEqual(key, 'B')

    def tearDown(self):
        del self.dict1
        del self.dict2

if __name__ == '__main__':
    unittest.main()
