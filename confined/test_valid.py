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
fparse = lambda rpn : str(parse(dict(
        a=1,
        b=2,
        a_string = "a beautiful world Isint ?",
        test = "test",
        ),rpn))


class TestCheck_Arg(unittest.TestCase):

    def test_first(self):
        self.assertEqual(feval("2: 2: ADD"), "4.0")

    def test_2(self):
        self.assertEqual(fparse("""1: "2": TAG >STR DUP """), '"1.0":2')

if __name__ == '__main__':
    unittest.main(verbosity=7)
