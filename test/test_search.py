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
from pycaching.search import Sorting, Origin

# logging.root.setLevel(logging.DEBUG)


def is_sorted(lst, key=lambda x: x, ascend=True):
    for i, el in enumerate(lst[1:]):
        if ascend:
            if key(el) <= key(lst[i]):  # i is the index of the previous element
                return False
        else:
            if key(el) >= key(lst[i]):  # i is the index of the previous element
                return False
    return True


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
                results = self.gc.search_advanced(Origin(Point(38.5314833, -28.63125), radius=10))
                for index, item in enumerate(results):
                    print("{} {} {}".format(index+1, item, item.name))
                self.assertEqual(index + 1, 62)

        with self.subTest("with_radius_imperial"):
            with self.recorder.use_cassette('search_with_radius_imperial'):
                results = self.gc.search_advanced(Origin( (38.5314833, -28.63125), radius=5, unit=Origin.UnitSystem.imperial))
                for index, item in enumerate(results):
                    print("{} {} {}".format(index+1, item, item.name))
                self.assertEqual(index + 1, 45)

        with self.subTest("top10"):
            with self.recorder.use_cassette('search_top10'):
                s = Sorting(Sorting.Columns.Favorites, Sorting.Order.descending)
                results = self.gc.search_advanced(sorting=s, limit=10)
                data = {}
                favorites = []
                for index, item in enumerate(results):
                    print("{} {} {} {}".format(index+1, item.wp, item.name, item.favorites))
                    data[item.wp] = item.favorites
                    favorites.append(item.favorites)
                print(data)
                self.assertTrue(is_sorted(favorites, ascend=False))
                self.assertEqual(index + 1, 10)
                self.assertDictEqual(data, {
                    'GC13Y2Y': 11360,
                    'GC11JM6': 8159,
                    'GC18182': 6811,
                    'GC2586K': 6795,
                    'GC167KK': 6362,
                    'GC38DP9': 5501,
                    'GC2J9J5': 5309,
                    'GC35KGZ': 5288,
                    'GC40': 5120,
                    'GCK25B': 4942
                })
        pass
