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
from pycaching.search import Sorting, Origin, Filter

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


class TestHelperObjects(unittest.TestCase):
    def test_origin(self):
        with self.subTest("worldwide (no origin)"):
            o = Origin()
            self.assertDictEqual(o.parameters, {'ot': '4'})
            o = Origin(radius=34)
            self.assertDictEqual(o.parameters, {'ot': '4'})
            o = Origin(unit=Origin.UnitSystem.imperial)
            self.assertDictEqual(o.parameters, {'ot': '4'})

        with self.subTest("origin"):
            o = Origin(Point(-51.7292, -59.2135))
            self.assertDictEqual(o.parameters, {'origin': '-51.7292, -59.2135'})
            o = Origin((-51.7292, -59.2135))
            self.assertDictEqual(o.parameters, {'origin': '-51.7292, -59.2135'})
            o = Origin([-51.7292, -59.2135])
            self.assertDictEqual(o.parameters, {'origin': '-51.7292, -59.2135'})

        with self.subTest("radius"):
            o = Origin((-51.7292, -59.2135), radius=5)
            self.assertDictEqual(o.parameters, {'origin': '-51.7292, -59.2135', 'radius': '5km'})

        with self.subTest("imperial"):
            o = Origin((-51.7292, -59.2135), radius=5, unit=Origin.UnitSystem.imperial)
            self.assertDictEqual(o.parameters, {'origin': '-51.7292, -59.2135', 'radius': '5mi'})

    def test_sorting(self):
        with self.subTest("without parameters"):
            s = Sorting()
            self.assertDictEqual(s.parameters, {})

        with self.subTest("order without column"):
            s = Sorting(order=Sorting.Order.descending)
            self.assertDictEqual(s.parameters, {})

        with self.subTest("column"):
            s = Sorting(Sorting.Columns.Favorites)
            self.assertDictEqual(s.parameters, {'sort': 'FavoritePoint', 'asc': 'True'})

        with self.subTest("column and order"):
            s = Sorting(Sorting.Columns.Favorites, Sorting.Order.descending)
            self.assertDictEqual(s.parameters, {'sort': 'FavoritePoint', 'asc': 'False'})
            s = Sorting(Sorting.Columns.Favorites, Sorting.Order.ascending)
            self.assertDictEqual(s.parameters, {'sort': 'FavoritePoint', 'asc': 'True'})

    def test_filter_range(self):
        with self.subTest("not set"):
            f = Filter(terrain=None)
            self.assertEqual(f.parameters, {})
            self.assertEqual(f.terrain, None)

        with self.subTest("single int"):
            f = Filter(terrain=1)
            self.assertEqual(f.parameters, {'t': '1'})
            self.assertEqual(f.terrain, 1.0)

        with self.subTest("single float"):
            f = Filter(terrain=1.0)
            self.assertEqual(f.parameters, {'t': '1'})
            self.assertEqual(f.terrain, 1.0)

        with self.subTest("single float"):
            f = Filter(terrain=1.7)
            self.assertEqual(f.parameters, {'t': '1.5'})
            self.assertEqual(f.terrain, 1.5)

        with self.subTest("single string(int)"):
            f = Filter(terrain="1")
            self.assertEqual(f.parameters, {'t': '1'})
            self.assertEqual(f.terrain, 1.0)

        with self.subTest("single string(float)"):
            f = Filter(terrain="1.0")
            self.assertEqual(f.parameters, {'t': '1'})
            self.assertEqual(f.terrain, 1.0)

        with self.subTest("single float / max-value"):
            f = Filter(terrain=4.5)
            self.assertEqual(f.parameters, {'t': '4.5'})
            self.assertEqual(f.terrain, 4.5)

        with self.subTest("single string(float) / max-value"):
            f = Filter(terrain="4.5")
            self.assertEqual(f.parameters, {'t': '4.5'})
            self.assertEqual(f.terrain, 4.5)

        with self.subTest("tuple"):
            f = Filter(terrain=(1, 5))
            self.assertEqual(f.parameters, {'t': '1-5'})
            self.assertEqual(f.terrain, (1.0, 5.0))

        with self.subTest("tuple - reverse"):
            f = Filter(terrain=(5, 1))
            self.assertEqual(f.parameters, {'t': '1-5'})
            self.assertEqual(f.terrain, (1.0, 5.0))

        with self.subTest("tuple - equal"):
            f = Filter(terrain=(3, 3))
            self.assertEqual(f.parameters, {'t': '3'})
            self.assertEqual(f.terrain, 3)

        with self.subTest("tuple - string & float"):
            f = Filter(terrain=("4.5", 1.5))
            self.assertEqual(f.parameters, {'t': '1.5-4.5'})
            self.assertEqual(f.terrain, (1.5, 4.5))

        with self.subTest("list"):
            f = Filter(terrain=[3.5, "2.5"])
            self.assertEqual(f.parameters, {'t': '2.5-3.5'})
            self.assertEqual(f.terrain, (2.5, 3.5))

    def test_filter_bool(self):
        with self.subTest("not set"):
            f = Filter(found=None)
            self.assertEqual(f.parameters, {})
            self.assertEqual(f.found, None)

        with self.subTest("false"):
            f = Filter(found=False)
            self.assertEqual(f.parameters, {'f': '2'})
            self.assertEqual(f.found, False)

        with self.subTest("true"):
            f = Filter(found=True)
            self.assertEqual(f.parameters, {'f': '1'})
            self.assertEqual(f.found, True)

        with self.subTest("zero"):
            f = Filter(found=0)
            self.assertEqual(f.parameters, {'f': '2'})
            self.assertEqual(f.found, False)

        with self.subTest("positive"):
            f = Filter(found=42)
            self.assertEqual(f.parameters, {'f': '1'})
            self.assertEqual(f.found, True)

    def test_filter(self):
        with self.subTest("empty filter"):
            f = Filter()
            self.assertEqual(f.parameters, {})

        with self.subTest("terrain & difficulty"):
            f = Filter(terrain=(1, 5), difficulty=(5, 1))
            self.assertEqual(f.parameters, {'t': '1-5', 'd': '1-5'})
            self.assertEqual(f.terrain, (1.0, 5.0))
            self.assertEqual(f.difficulty, (1.0, 5.0))

        with self.subTest("Personal Note"):
            f = Filter(personal_note=None)
            self.assertEqual(f.parameters, {})
            self.assertEqual(f.personal_note, None)

            f = Filter(personal_note=False)
            self.assertEqual(f.parameters, {'note': '2'})
            self.assertEqual(f.personal_note, False)

            f = Filter(personal_note=True)
            self.assertEqual(f.parameters, {'note': '1'})
            self.assertEqual(f.personal_note, True)

        with self.subTest("Corrected Coordinates"):
            f = Filter(corrected_coordinates=None)
            self.assertEqual(f.parameters, {})
            self.assertEqual(f.corrected_coordinates, None)

            f = Filter(corrected_coordinates=False)
            self.assertEqual(f.parameters, {'cc': '2'})
            self.assertEqual(f.corrected_coordinates, False)

            f = Filter(corrected_coordinates=True)
            self.assertEqual(f.parameters, {'cc': '1'})
            self.assertEqual(f.corrected_coordinates, True)

        with self.subTest("Membership type"):
            f = Filter(premium=None)
            self.assertEqual(f.parameters, {})
            self.assertEqual(f.premium, None)

            f = Filter(premium=False)
            self.assertEqual(f.parameters, {'p': '2'})
            self.assertEqual(f.premium, False)

            f = Filter(premium=True)
            self.assertEqual(f.parameters, {'p': '1'})
            self.assertEqual(f.premium, True)

        with self.subTest("Minimum Favorite Points"):
            f = Filter(favorite_points=None)
            self.assertEqual(f.parameters, {})
            self.assertEqual(f.favorite_points, None)

            f = Filter(favorite_points=4711)
            self.assertEqual(f.parameters, {'fav': '4711'})
            self.assertEqual(f.favorite_points, 4711)
            self.assertEqual(type(f.favorite_points), int)

            f = Filter(favorite_points=4711.42)
            self.assertEqual(f.parameters, {'fav': '4711'})
            self.assertEqual(type(f.favorite_points), int)

            f = Filter(favorite_points="4711")
            self.assertEqual(f.parameters, {'fav': '4711'})
            self.assertEqual(f.favorite_points, 4711)
            self.assertEqual(type(f.favorite_points), int)

        with self.subTest("Ownership"):
            f = Filter(owner=None)
            self.assertEqual(f.parameters, {})
            self.assertEqual(f.owner, None)

            f = Filter(owner=False)
            self.assertEqual(f.parameters, {'o': '2'})
            self.assertEqual(f.owner, False)
            self.assertEqual(type(f.owner), bool)

            f = Filter(owner=True)
            self.assertEqual(f.parameters, {'o': '1'})
            self.assertEqual(f.owner, True)
            self.assertEqual(type(f.owner), bool)

        with self.subTest("Keyword"):
            f = Filter(keyword=None)
            self.assertEqual(f.parameters, {})
            self.assertEqual(f.keyword, None)

            f = Filter(keyword='fox')
            self.assertEqual(f.parameters, {'kw': 'fox'})
            self.assertEqual(f.keyword, 'fox')
            self.assertEqual(type(f.keyword), str)

            f = Filter(keyword=3.141592)
            self.assertEqual(f.parameters, {'kw': '3.141592'})
            self.assertEqual(f.keyword, '3.141592')
            self.assertEqual(type(f.keyword), str)

        with self.subTest("Hidden by"):
            f = Filter(hidden=None)
            self.assertEqual(f.parameters, {})
            self.assertEqual(f.hidden, None)

            f = Filter(hidden="Geocaching HQ")
            self.assertEqual(f.parameters, { 'owner[0]': 'Geocaching HQ'})
            self.assertEqual(f.hidden, 'Geocaching HQ')
            self.assertEqual(type(f.hidden), str)

            f = Filter(hidden=123)
            self.assertEqual(f.parameters, { 'owner[0]': '123'})
            self.assertEqual(f.hidden, '123')
            self.assertEqual(type(f.hidden), str)

