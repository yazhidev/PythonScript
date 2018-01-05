# coding=utf-8

import unittest

def hello():
    return "hello world"

class testNum(unittest.TestCase):
    def testHello(self):
        self.assertEqual("hello world",hello())

    def testHello2(self):
        self.assertEqual("hello world2",hello())

if __name__ == '__main__':
    # unittest.main()
    #可打印出方法名
    suite = unittest.TestLoader().loadTestsFromTestCase(testNum)
    unittest.TextTestRunner(verbosity=3).run(suite)

# assertEqual(a, b) a == b
# assertNotEqual(a, b) a != b
# assertTrue(x) bool(x) is True
# assertFalse(x) bool(x) is False
# assertIs(a, b) a is b 2.7
# assertIsNot(a, b) a is not b 2.7
# assertIsNone(x) x is None 2.7
# assertIsNotNone(x) x is not None 2.7
# assertIn(a, b) a in b 2.7
# assertNotIn(a, b) a not in b 2.7
# assertIsInstance(a, b) isinstance(a, b) 2.7
# assertNotIsInstance(a, b) not isinstance(a, b) 2.7