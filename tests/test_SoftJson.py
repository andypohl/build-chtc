'''Tests for that dictionary class I found on on the internet.'''

import unittest2 as unittest
import sys
from chtc import SoftJson

class TestSoftJson(unittest.TestCase):
    '''Tests for SoftJson'''
    def setUp(self):
        self.empty = SoftJson()
        self.turtle = SoftJson()

    def test_good_json(self):
        # Remember to include *this* subdir in relative path because nose2
        # is executed from parent dir.
        self.empty.add_json_file("tests/data/good.json")
        pass

    def test_bfs(self):
        # This is an important that tackles a few of the issues when multiple versions of the same
        # software are encountered in a dependency tree.  The algorithm is supposed to favor the 
        # version at the higher level in the tree, closest to the main software being compiled
        # 
        #            turtle-1.0
        #          /      |     \ 
        #    bird-1.2  fox-3.2    cow-1.7
        #      |                  /      \
        #    dog-4.0          bird-1.0   cat-2.1
        #                        |
        #                     dog-3.0
        # 
        # the bird-1.0 lineage should be replaced by bird-1.2's.  cat-2.1 is built between bird-1.2
        # and dog-3.0 because dependency order, although unimportant, is consistent.
        self.turtle.add_json_file('tests/data/turtle.json')
        soft_list = self.turtle.get_deps_bfs('turtle-1.0')
        self.assertIsNotNone(soft_list)
        self.assertEquals(6, len(soft_list))
        self.assertEquals('dog-4.0', soft_list[0].get_prefix())
        self.assertEquals('cat-2.1', soft_list[1].get_prefix())
        self.assertEquals('bird-1.2', soft_list[2].get_prefix())
        self.assertEquals('cow-1.7', soft_list[3].get_prefix())
        self.assertEquals('fox-3.2', soft_list[4].get_prefix())
        self.assertEquals('turtle-1.0', soft_list[5].get_prefix())

    def tearDown(self):
        del self.empty
        del self.turtle
