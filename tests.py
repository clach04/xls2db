#!/usr/bin/env python
# -*- coding: ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
"""Test suite for xls2db
"""

import os
import sys
import sqlite3

try:
    if sys.version_info < (2, 3):
        raise ImportError
    import unittest2
    unittest = unittest2
except ImportError:
    import unittest
    unittest2 = None

import xls2db


def do_one(xls_filename, dbname):
    xls2db.xls2db(xls_filename, dbname)


class AllTests(unittest.TestCase):
    def test_comma(self):
        xls_filename, dbname = 'comma_test.xls', ':memory:'
        # For now just see if it works without error
        do_one(xls_filename, dbname)


def main():
    # Some tests may use data files (without a full pathname)
    # set current working directory to test directory if
    # test is not being run from the same directory
    testpath = os.path.dirname(__file__)
    if testpath:
        testpath = os.path.join(testpath, 'example')
    else:
        # Just assume current directory
        testpath = 'example'
    try:
        os.chdir(testpath)
    except OSError:
        # this may be Jython 2.2 under OpenJDK...
        if sys.version_info <= (2, 3):
            pass
        else:
            raise
    unittest.main()

if __name__ == '__main__':
    main()