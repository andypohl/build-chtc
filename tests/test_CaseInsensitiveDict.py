'''Tests for that dictionary class I found on on the internet.'''

from chtc import CaseInsensitiveDict

class TestCaseInsensitiveDict(unittest.TestCase):
    '''Tests for CaseInsensitiveDict'''
    def setUp(self):
        self.dict1 = CaseInsensitiveDict({'A': 4, 'B': 3, 'C': 2})
        self.dict2 = CaseInsensitiveDict({'a': 4, 'b': 3, 'c': 2})

    def test_keys(self):
        '''Test some ways to key into the dictionary'''
        self.assertTrue(self.dict1.has_key('A'))
        self.assertTrue(self.dict1.has_key('a'))
        self.assertTrue(self.dict2.has_key('A'))
        self.assertTrue(self.dict2.has_key('a'))
        self.assertFalse(self.dict2.has_key('D'))
        with self.assertRaises(KeyError):
            self.dict2['D']
        with self.assertRaises(KeyError):
            self.dict2['d']

    def test_lookup(self):
        '''Look up things in the dictionary.'''
        self.assertEqual(self.dict1['C'], 2)
        self.assertEqual(self.dict1['c'], 2)
        self.assertEqual(self.dict1['c'], self.dict2['c'])
        self.assertNotEqual(self.dict1['b'], 12)

    @unittest.skipIf(sys.version_info < (2,7))
    def test_misc(self):
        '''A few other misc tests.'''
        # this seems really hacky
        if 'assertDictEqual' in dir(self):
            self.assertDictEqual(self.dict1, self.dict2)

    def tearDown(self):
        del self.dict1
        del self.dict2

if __name__ == '__main__':
    unittest.main()
