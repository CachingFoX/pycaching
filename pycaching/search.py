import enum
from pycaching.geo import Point


class UrlParameters():
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
        :param search.SortColumn sort_column: Defines the search column
        :param sort_ascend: True (None) means ascend, False means descend
        """
        super().__init__()
        # TODO raise excpetion if login user basic member and sort_column is given
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
        :param bool imperial: If it True, radius in handle as miles instead of kilometers.

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


class Filter(UrlParameters):
    def __init__(self, enabled=None, found=None, terrain=None, difficulty=None):
        """

        :param enabled:
        :param found:
        """
        super().__init__()
        self._raw_parameters = {}

        self.enabled = enabled
        self.found = found
        self.terrain = terrain
        self.difficulty = difficulty

    def __helper_get_bool(self, name):
        if name not in self._parameters:
            return None  # TODO check if raise KeyError is better ???
        else:
            if self._parameters[name] == '2':
                return False
            elif self._parameters[name] == '1':
                return True
            else:
                return None

    def __helper_set_bool(self, name, value):
        if value is not None:
            if type(value) != bool:
                value = bool(value)

            self._parameters[name] = '1' if value else '2'
        else:
            self.remove_parameters(name)

    def __helper_get_range(self, name):
        if name not in self._parameters:
            return None
        else:
            return self._raw_parameters[name]

    def __helper_set_range(self, name, value):
        """
        Convert a 1-5 star range with 0.5 steps into a string

        :param name:
        :param value:
        :return:
        """
        if value is None:
            if name in self._raw_parameters:
                del self._raw_parameters[name]
            self.remove_parameters(name)
            return

        if type(value) == int or type(value) == float or type(value) == str:
            value = (float(value), float(value))  # convert int or float value into a tuple

        if type(value) == list:
            value = tuple(i for i in value)

        if type(value) != tuple:  # TODO check for list
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
            self._result = '{0}-{1}'.format(v0, v1)
            self._raw_parameters[name] = (v0, v1)
        elif v0 > v1:
            self._result = '{0}-{1}'.format(v1, v0)
            self._raw_parameters[name] = (v1, v0)
        else:
            self._result = str(v0)
            self._raw_parameters[name] = v0

        self._parameters[name] = self._result.replace('.0', '')  # remove .0 from string


    @property
    def enabled(self):
        return self.__helper_get_bool('e')

    @enabled.setter
    def enabled(self, value):
        return self.__helper_set_bool('e', value)

    @property
    def found(self):
        return self.__helper_get_bool('f')

    @found.setter
    def found(self, value):
        return self.__helper_set_bool('f', value)

    @property
    def terrain(self):
        return self.__helper_get_range('t')

    @terrain.setter
    def terrain(self, value):
        return self.__helper_set_range('t', value)

    @property
    def difficulty(self):
        return self.__helper_get_range('d')

    @difficulty.setter
    def difficulty(self, value):
        return self.__helper_set_range('d', value)

