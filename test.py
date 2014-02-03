# -*- coding: utf-8 -*-
import os
import sys
import re
import sqlite3 as sqlite

try:
    if sys.version_info < (2, 3):
        raise ImportError
    import unittest2
    unittest = unittest2
except ImportError:
    import unittest
    unittest2 = None

import xls2db


def do_one(xls_filename, dbname, do_drop=False):
    if do_drop:
        xls2db.xls2db(xls_filename, dbname, do_drop=do_drop)
    else:
        xls2db.xls2db(xls_filename, dbname)


class AllTests(unittest.TestCase):
    def test_stackhaus(self):
        xls_filename, dbname = 'stackhaus.xls', 'stackhaus.db'
        try:
            os.remove(dbname)
        except:
            pass

        do_one(xls_filename, dbname)

        stackhaus = sqlite.connect(dbname)

        tests = {
            "locations": [
                "id string primary key",
                "short_descr string",
                "long_descr string",
                "special string"
            ],
            "links": [
                "src string",
                "dst string",
                "dir string"
            ],
            "items": [
                "id string primary key",
                "location string",
                "short_descr string",
                "long_descr string",
                "get_descr string",
                "get_pts integer",
                "use_desc string",
                "use_pts integer"
            ]
        }

        for t in tests.items():
            table = t[0]
            headers = t[1]

            row = stackhaus.execute(
                "SELECT sql FROM sqlite_master WHERE tbl_name = ? AND type = 'table'", (table,)
            ).fetchone()

            for header in headers:
                msg = u'header ' + header + u' in ' + table
                self.assertTrue(re.search(header, row[0]), 'x ' + msg)

    def test_comma(self):
        xls_filename, dbname = 'comma_test.xls', ':memory:'
        db = sqlite.connect(dbname)
        try:
            c = db.cursor()
            do_one(xls_filename, db)
            c.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'")
            rows = c.fetchall()
            self.assertEqual(rows, [(u'comma_test',)])

            c.execute("SELECT * FROM comma_test ORDER BY 1")
            rows = c.fetchall()
            col_names = []
            for c_description in c.description:
                col_names.append(c_description[0])
            self.assertEqual(col_names, [u'col1', u'english, text'])
            self.assertEqual(rows, [(1.0, u'one'), (2.0, u'two'), (3.0, u'three')])
        finally:
            db.close()

    def test_empty_worksheet(self):
        xls_filename, dbname = 'empty_worksheet_test.xls', ':memory:'
        db = sqlite.connect(dbname)
        try:
            c = db.cursor()
            do_one(xls_filename, db)
            c.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'")
            rows = c.fetchall()
            self.assertEqual(rows, [(u'simple_test',)])
        finally:
            db.close()

    def test_simple_test(self):
        xls_filename, dbname = 'simple_test.xls', ':memory:'
        db = sqlite.connect(dbname)
        try:
            c = db.cursor()
            do_one(xls_filename, db)
            c.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'")
            rows = c.fetchall()
            self.assertEqual(rows, [(u'simple_test',)])

            c.execute("SELECT * FROM simple_test ORDER BY 1")
            rows = c.fetchall()
            self.assertEqual(rows, [(1.0, u'one'), (2.0, u'two'), (3.0, u'three')])
        finally:
            db.close()

    def test_simple_test_twice(self):
        xls_filename, dbname = 'simple_test.xls', ':memory:'
        db = sqlite.connect(dbname)
        c = db.cursor()

        def do_one_simple_conversion():
            do_one(xls_filename, db)
            c.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'")
            rows = c.fetchall()
            self.assertEqual(rows, [(u'simple_test',)])

            c.execute("SELECT * FROM simple_test ORDER BY 1")
            rows = c.fetchall()
            self.assertEqual(rows, [(1.0, u'one'), (2.0, u'two'), (3.0, u'three')])

        try:
            do_one_simple_conversion()
            self.assertRaises(sqlite.OperationalError, do_one_simple_conversion)
        finally:
            db.close()

    def test_simple_test_twice_with_drop(self):
        xls_filename, dbname = 'simple_test.xls', ':memory:'
        db = sqlite.connect(dbname)
        c = db.cursor()

        def do_one_simple_conversion():
            do_one(xls_filename, db, do_drop=True)
            c.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'")
            rows = c.fetchall()
            self.assertEqual(rows, [(u'simple_test',)])

            c.execute("SELECT * FROM simple_test ORDER BY 1")
            rows = c.fetchall()
            self.assertEqual(rows, [(1.0, u'one'), (2.0, u'two'), (3.0, u'three')])

        try:
            do_one_simple_conversion()
            do_one_simple_conversion()  # do again
        finally:
            db.close()


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
