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

# logging.root.setLevel(logging.DEBUG)

class TestMethods(NetworkedTest):
    def test_search(self):
        # https://github.com/tomasbedrich/pycaching/issues/144
        '''
        parameter limit have to be bigger then the number of results

        '''
        # return
        with self.recorder.use_cassette('search-issue-144'):
            results = self.gc.search(Point(38.5314833, -28.63125), limit=150)
            for item in results:
                print(item, item.size)

            '''    
            finds = list(self.gc.my_finds(20))
            self.assertEqual(20, len(finds))
            for cache in finds:
                self.assertTrue(cache.name)
                self.assertTrue(isinstance(cache, Cache))
            '''

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

    '''
    def test_search(self):
        with self.subTest("normal"):
            tolerance = 2
            expected = {"GC5VJ0P", "GC41FJC", "GC17E8Y", "GC14AV5", "GC50AQ6", "GC167Y7"}
            with self.recorder.use_cassette('geocaching_search'):
                found = {cache.wp for cache in self.gc.search(Point(49.733867, 13.397091), 20)}
            self.assertGreater(len(expected & found), len(expected) - tolerance)

        with self.subTest("pagging"):
            with self.recorder.use_cassette('geocaching_search_pagination'):
                caches = list(self.gc.search(Point(49.733867, 13.397091), 100))
            self.assertNotEqual(caches[0], caches[50])
    '''
    '''
    @unittest.expectedFailure
    def test_search_quick(self):
        """Perform quick search and check found caches"""
        # at time of writing, there were exactly 16 caches in this area + one PM only
        expected_cache_num = 16
        tolerance = 7
        rect = Rectangle(Point(49.73, 13.38), Point(49.74, 13.40))

        with self.subTest("normal"):
            with self.recorder.use_cassette('geocaching_quick_normal'):
                # Once this feature is fixed, the corresponding cassette will have to be deleted
                # and re-recorded.
                res = [c.wp for c in self.gc.search_quick(rect)]
            for wp in ["GC41FJC", "GC17E8Y", "GC383XN"]:
                self.assertIn(wp, res)
            # but 108 caches larger tile
            self.assertLess(len(res), 130)
            self.assertGreater(len(res), 90)

        with self.subTest("strict handling of cache coordinates"):
            with self.recorder.use_cassette('geocaching_quick_strictness'):
                res = list(self.gc.search_quick(rect, strict=True))
            self.assertLess(len(res), expected_cache_num + tolerance)
            self.assertGreater(len(res), expected_cache_num - tolerance)

        with self.subTest("larger zoom - more precise"):
            with self.recorder.use_cassette('geocaching_quick_zoom'):
                res1 = list(self.gc.search_quick(rect, strict=True, zoom=15))
                res2 = list(self.gc.search_quick(rect, strict=True, zoom=14))
            for res in res1, res2:
                self.assertLess(len(res), expected_cache_num + tolerance)
                self.assertGreater(len(res), expected_cache_num - tolerance)
            for c1, c2 in itertools.product(res1, res2):
                self.assertLess(c1.location.precision, c2.location.precision)

    @unittest.expectedFailure
    def test_search_quick_match_load(self):
        """Test if quick search results matches exact cache locations."""
        rect = Rectangle(Point(49.73, 13.38), Point(49.74, 13.39))
        with self.recorder.use_cassette('geocaching_matchload'):
            # at commit time, this test is an allowed failure. Once this feature is fixed, the
            # corresponding cassette will have to be deleted and re-recorded.
            caches = list(self.gc.search_quick(rect, strict=True, zoom=15))
            for cache in caches:
                try:
                    cache.load()
                    self.assertIn(cache.location, rect)
                except PMOnlyException:
                    pass

    def test__try_getting_cache_from_guid(self):
        # get "normal" cache from guidpage
        with self.recorder.use_cassette('geocaching_shortcut_getcache__by_guid'):  # is a replacement for login
            cache = self.gc._try_getting_cache_from_guid('15ad3a3d-92c1-4f7c-b273-60937bcc2072')
            self.assertEqual("Nekonecne ticho", cache.name)

        # get PMonly cache from GC code (doesn't load any information)
        cache_pm = self.gc._try_getting_cache_from_guid('328927c1-aa8c-4e0d-bf59-31f1ce44d990')
        cache_pm.load_quick()  # necessary to get name for PMonly cache
        self.assertEqual("Nidda: jenseits der Rennstrecke Reloaded", cache_pm.name)
    '''

