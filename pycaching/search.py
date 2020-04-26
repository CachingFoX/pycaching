import enum
from pycaching.geo import Point


class UrlParameters:
    def __init__(self):
        self._parameters = {}

    def __repr__(self):
        return "{}".format(self._parameters)

    @property
    def parameters(self):
        return self._parameters

    def add_parameters(self, name, value):
        if type(name) != str:
            raise TypeError
        if value is None:
            raise ValueError
        self._parameters[name] = value

    def remove_parameters(self, name):
        if type(name) != str:
            raise TypeError
        if name in self._parameters:
            del self._parameters[name]


class Sorting(UrlParameters):
    class Columns(enum.Enum):
        """
        Enum of possible columns to sort.

        """

        Distance = "Distance"
        Favorites = "FavoritePoint"
        Size = "ContainerSize"
        Difficulty = "Difficulty"
        Terrain = "Terrain"
        Last_Found = "DateLastVisited"
        Placed_On = "PlaceDate"

        def __str__(self):
            return self.value

    class Order(enum.Enum):
        """
        Enum of possible sorting orders.

        """
        ascending = "True"
        descending = "False"

        def __str__(self):
            return self.value

    def __init__(self, column=None, order=Order.ascending):
        """

        :param column:
        :param order:
        :param column: Defines the search column
        :param order: Defines the sort order (default: ascending)
        """
        super().__init__()
        # TODO raise exception if login user basic member and sort_column is given
        if column is not None:

            if type(column) != Sorting.Columns or type(order) != Sorting.Order:
                raise TypeError

            self._parameters['sort'] = str(column)
            self._parameters['asc'] = str(order)


class Origin(UrlParameters):
    class UnitSystem(enum.Enum):
        """
        Enum of possible sorting orders.

        """
        metric = "km"
        imperial = "mi"

        def __str__(self):
            return self.value

    def __init__(self, point=None, radius=None, unit=UnitSystem.metric):
        """
        :param point: Search center point (optional)
        :param int radius: Search radius in kilometers or miles (see also parameter imperial)
        :param UnitSystem unit: defines the unit system (default: metric).

        Parameter point can be a None, geo.Point object, a tuple or list with two floats as latitude and longitude
        """
        super().__init__()

        if point is None:
            self._parameters['ot'] = '4'
        else:
            if type(point) != Point:
                point = Point(point)

            assert hasattr(point, "format") and callable(point.format)
            self._parameters['origin'] = point.format_decimal()

            if radius is not None:
                radius = int(radius)
                if radius < 1:
                    raise ValueError
                self._parameters['radius'] = '{}{}'.format(int(radius), str(unit))


class Filter:
    def __init__(self, enabled=None, found=None, terrain=None, difficulty=None, personal_note=None,
                 corrected_coordinates=None, premium=None, favorite_points=None, owner=None):
        """

        :param enabled:
        :param found:
        """
        self._parameters = {
            'enabled': None,
            'found': None,
            'terrain': None,
            'difficulty': None,
            'personal_note': None,
            'corrected_coordinates': None,
            'premium': None,
            'favorite_points': None,
            'owner': None
        }

        self.enabled = enabled
        self.found = found
        self.terrain = terrain
        self.difficulty = difficulty
        self.personal_note = personal_note
        self.corrected_coordinates = corrected_coordinates
        self.premium = premium
        self.favorite_points = favorite_points
        self.owner = owner

    def __repr__(self):
        return "{}".format(self.parameters)

    @property
    def parameters(self):
        q = {
            't': self.__helper_get_range(self.terrain),
            'd': self.__helper_get_range(self.difficulty),
            'f': self.__helper_get_bool(self.found),
            'e': self.__helper_get_bool(self.enabled),
            'note': self.__helper_get_bool(self.personal_note),
            'cc': self.__helper_get_bool(self.corrected_coordinates),
            'p': self.__helper_get_bool(self.premium),
            'fav': str(self.favorite_points) if self.favorite_points is not None else None,
            'o': self.__helper_get_bool(self.owner)
        }
        # remove all items in the dict with the value None
        for key in list(q):
            if q[key] is None:
                del q[key]

        return q

    #@staticmethod
    def __helper_get_bool(self, value):
        if value is None:
            return None
        return '1' if value else '2'

    def __helper_set_bool(self, name, value):
        if value is not None and type(value) != bool:
            value = bool(value)
        self._parameters[name] = value

    # @staticmethod
    def __helper_get_range(self, value):
        if value is None:
            return None

        if type(value) == tuple:
            result = '{0}-{1}'.format(value[0], value[1])
        else:
            result = str(value)

        return result.replace('.0', '')  # remove .0 from string

    def __helper_set_range(self, name, value):
        """
        Convert a 1-5 star range with 0.5 steps into a string

        :param name:
        :param value:
        :return:
        """
        if value is None:
            self._parameters[name] = None
            return

        if type(value) == int or type(value) == float or type(value) == str:
            value = (float(value), float(value))  # convert int or float value into a tuple

        if type(value) == list:
            value = tuple(i for i in value)

        if type(value) != tuple:
            raise TypeError("expected a tuple, int, float, str")

        if len(value) != 2:
            raise ValueError("expected tuple with one or two items")

        v0 = int(float(value[0]) * 2) / 2  # only steps of 0.5 are allowed
        if not (1 <= v0 <= 5):
            raise ValueError('Value ({0}) is out of range.'.format(value[0]))

        v1 = int(float(value[1]) * 2) / 2  # only steps of 0.5 are allowed
        if not (1 <= v1 <= 5):
            raise ValueError('Value ({0}) is out of range.'.format(value[1]))

        if v0 < v1:
            self._parameters[name] = (v0, v1)
        elif v0 > v1:
            self._parameters[name] = (v1, v0)
        else:
            self._parameters[name] = v0

    @property
    def enabled(self):
        return self._parameters['enabled']

    @enabled.setter
    def enabled(self, value):
        self.__helper_set_bool('enabled', value)

    @property
    def found(self):
        return self._parameters['found']

    @found.setter
    def found(self, value):
        self.__helper_set_bool('found', value)

    @property
    def terrain(self):
        return self._parameters['terrain']

    @terrain.setter
    def terrain(self, value):
        self.__helper_set_range('terrain', value)

    @property
    def difficulty(self):
        return self._parameters['difficulty']

    @difficulty.setter
    def difficulty(self, value):
        self.__helper_set_range('difficulty', value)

    @property
    def personal_note(self):
        return self._parameters['personal_note']

    @personal_note.setter
    def personal_note(self,value):
        self.__helper_set_bool('personal_note', value)

    @property
    def corrected_coordinates(self):
        return self._parameters['corrected_coordinates']

    @corrected_coordinates.setter
    def corrected_coordinates(self, value):
        self.__helper_set_bool('corrected_coordinates', value)

    @property
    def premium(self):
        return self._parameters['premium']

    @premium.setter
    def premium(self, value):
        self.__helper_set_bool('premium', value)

    @property
    def favorite_points(self):
        return self._parameters['favorite_points']

    @favorite_points.setter
    def favorite_points(self, value):
        if value is not None:
            value = int(value)
        self._parameters['favorite_points'] = value

    @property
    def owner(self):
        return self._parameters['owner']

    @owner.setter
    def owner(self, value):
        self.__helper_set_bool('owner', value)
