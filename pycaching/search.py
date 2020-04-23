
class Filter:
    def __init__(self, enabled=None, found=None):
        """

        :param enabled:
        :param found:
        """
        self._parameters = {}
        self.enabled = enabled
        self.found = found

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

    def __helper_get_bool(self, name):
        if name not in self._parameters:
            return None
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



