import enum
from pycaching.geo import Point


class UrlParameters():
    def __init__(self):
        self._parameters = {}

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

    def __repr__(self):
        if 'sort' not in self._parameters:
            return "no sorting order"
        else:
            return "column={} ascending={}".format(self._parameters['sort'], self._parameters['asc'])


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
            self._parameters['ot'] = 4
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

    def __repr__(self):
        if 'origin' not in self._parameters:
            return "no center"
        elif 'radius' not in self._parameters:
            return "{}".format(self._parameters['origin'])
        else:
            return "{} {}".format(self._parameters['origin'], self._parameters['radius'])


class Filter(UrlParameters):
    def __init__(self, enabled=None, found=None):
        """

        :param enabled:
        :param found:
        """
        super().__init__()
        self.enabled = enabled
        self.found = found

    def __helper_get_bool(self, name):
        if name not in self._parameters:
            return None  # TODO check if raise KeyError is better ???
        else:
            if self._parameters[name] == 1:
                return False
            elif self._parameters[name] == 2:
                return True
            else:
                return None

    def __helper_set_bool(self, name, value):
        if value is not None:
            if type(value) != bool:
                raise TypeError
            self._parameters[name] = '1' if value else '2'
        else:
            self.remove_parameters(name)

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
