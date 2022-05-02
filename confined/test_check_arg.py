#/usr/bin/env python
import os
import sys

import unittest
from .check_arg import valid_and_doc, default_doc_maker

class TestCheck_Arg(unittest.TestCase):
    def setUp(self):
        def must_have_key(*needed_keys):
            def must_have_key(*a,**kw):
                if not kw:
                    raise Exception("No keyword are provided")
                for key in needed_keys:
                    if not key in kw: 
                        raise Exception("%s is mandatory in keywords arguments" % key )
            return must_have_key
        
        def at_least_n_positional(how_many):
            def at_least_n_positional(*a, **kw):
                if len(a) < how_many:
                    raise Exception("too few arguments")
            return at_least_n_positional

        at_least = valid_and_doc(at_least_n_positional)
        must_have = valid_and_doc(must_have_key)

        @at_least(2)
        @must_have("name")
        def does_nothing(a=1,*b, **kw):
            """useless fonction"""
            return True
            
        self.test_me = does_nothing

    def test_doc_output(self):
        doc = self.test_me.__doc__ 
        self.assertEqual(doc, "useless fonction\n**must_have_key** :name\n\n\n**at_least_n_positional** :2\n\n")

    def test_valid(self):
        with self.assertRaises(Exception) as context:
            self.test_me(1,2,nime="")
        self.assertEqual(str(context.exception),"name is mandatory in keywords arguments")

    def test_valid2(self):
        with self.assertRaises(Exception) as context:
            self.test_me(1,)
        self.assertEqual(str(context.exception),"too few arguments")

if __name__ == '__main__':
    unittest.main(verbosity=7)
