#/usr/bin/env python
import os
import sys

import unittest
from confined import parse, templatize


feval = lambda rpn: templatize(dict(
        a=1,
        b=2,
        a_string = "a beautiful world Isint ?",

    ), "<: %s :>" % rpn 
)

class TestCheck_Arg(unittest.TestCase):

    def test_first(self):
        self.assertEqual(feval("2: 2: ADD"), "4.0")


if __name__ == '__main__':
    unittest.main(verbosity=7)
