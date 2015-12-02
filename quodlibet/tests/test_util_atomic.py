# -*- coding: utf-8 -*-
# Copyright 2013 Christoph Reiter
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

import os
import stat
import shutil

from tests import TestCase, mkdtemp

from quodlibet.util.atomic import atomic_save


class Tatomic_save(TestCase):

    def setUp(self):
        self.dir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_basic(self):
        filename = os.path.join(self.dir, "foo.txt")

        with open(filename, "wb") as fobj:
            fobj.write("nope")

        with atomic_save(filename, "wb") as fobj:
            fobj.write("foo")
            temp_name = fobj.name

        with open(filename, "rb") as fobj:
            self.assertEqual(fobj.read(), "foo")

        self.assertFalse(os.path.exists(temp_name))
        self.assertEqual(os.listdir(self.dir), [os.path.basename(filename)])

    def test_non_exist(self):
        filename = os.path.join(self.dir, "foo.txt")

        with atomic_save(filename, "wb") as fobj:
            fobj.write("foo")
            temp_name = fobj.name

        with open(filename, "rb") as fobj:
            self.assertEqual(fobj.read(), "foo")

        self.assertFalse(os.path.exists(temp_name))
        self.assertEqual(os.listdir(self.dir), [os.path.basename(filename)])

    def test_readonly(self):
        filename = os.path.join(self.dir, "foo.txt")

        with open(filename, "wb") as fobj:
            fobj.write("nope")

        mode = os.stat(self.dir).st_mode
        os.chmod(self.dir, stat.S_IREAD)
        try:
            with self.assertRaises(OSError):
                with atomic_save(filename, "wb") as fobj:
                    fobj.write("foo")
        finally:
            os.chmod(self.dir, mode)

        with open(filename, "rb") as fobj:
            self.assertEqual(fobj.read(), "nope")

        self.assertEqual(os.listdir(self.dir), [os.path.basename(filename)])
