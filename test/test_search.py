#!/usr/bin/env python3

import itertools
import json
import os
import unittest
from subprocess import CalledProcessError
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from geopy.distance import great_circle

import pycaching
from pycaching import Cache, Geocaching, Point, Rectangle
from pycaching.errors import NotLoggedInException, LoginFailedException, PMOnlyException
from . import username as _username, password as _password, NetworkedTest
import logging
from pycaching.search import SortColumn

# logging.root.setLevel(logging.DEBUG)

class TestMethods(NetworkedTest):
    def test_search(self):
        '''
        parameter limit have to be bigger then the number of results
        https://github.com/tomasbedrich/pycaching/issues/144
        '''
        with self.recorder.use_cassette('search-issue-144'):
            results = self.gc.search(Point(38.5314833, -28.63125), limit=150)
            for item in results:
                print(item, item.size)



    def test_search_advanced(self):
        with self.subTest("without_location"):
            with self.recorder.use_cassette('search_without_location'):
                results = self.gc.search_advanced(limit=150)
                for index, item in enumerate(results):
                    print("{} {} {}".format(index+1, item, item.name))
                self.assertEqual(index + 1, 150)

        with self.subTest("with_location"):
            with self.recorder.use_cassette('search_with_location'):
                results = self.gc.search_advanced(Point(38.5314833, -28.63125), limit=150)
                for index, item in enumerate(results):
                    print("{} {} {}".format(index+1, item, item.name))
                self.assertEqual(index+1, 105)

        with self.subTest("with_radius"):
            with self.recorder.use_cassette('search_with_radius'):
                results = self.gc.search_advanced(Point(38.5314833, -28.63125), radius=10)
                for index, item in enumerate(results):
                    print("{} {} {}".format(index+1, item, item.name))
                self.assertEqual(index + 1, 62)

        with self.subTest("with_radius_imperial"):
            with self.recorder.use_cassette('search_with_radius_imperial'):
                results = self.gc.search_advanced(Point(38.5314833, -28.63125), radius=5, imperial=True)
                for index, item in enumerate(results):
                    print("{} {} {}".format(index+1, item, item.name))
                self.assertEqual(index + 1, 45)
