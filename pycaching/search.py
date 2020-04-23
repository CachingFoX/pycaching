import enum


class SortColumn(enum.Enum):
    """
    Enum of possible cache sizes.

    Naming follows Groundspeak image filenames, values are human readable names.
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


