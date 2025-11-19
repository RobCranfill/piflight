"""
geographical stuff
not tested for southern hemisphere or eastern hemispheres
(that is, it works for positive latitude and negative longitude - all I care about!)
"""

class lat_long:
    """A lat/long pair."""
    def __init__(self, lat, long):
        self.lat = float(lat)
        self.long = float(long)

    def __str__(self):
        return f"({self.lat},{self.long})"

    def __repr__(self):
        """Used by {x=} formatting!"""
        return self.__str__()


class mapper:
    """Map a lat/long in a given region to a pixel position for a display."""

    def __init__(self, lat_long_upper_left, lat_long_lower_right, x_y_size):
        """lat_long, lat_long, (x,y)"""

        self._lat_long_upper_left  = lat_long_upper_left
        self._lat_long_lower_right = lat_long_lower_right
        self._x_y_size = x_y_size

    def map_lat_long_to_x_y(self, lat_long_pair):
        """Map the input geo loction to an (x,y) location."""

        lat_span = (self._lat_long_upper_left.lat - self._lat_long_lower_right.lat)
        lat_delta = self._lat_long_upper_left.lat - lat_long_pair.lat
        lat_frac =  lat_delta / lat_span
        y = self._x_y_size[1] * lat_frac

        long_span = (self._lat_long_upper_left.long - self._lat_long_lower_right.long)
        long_delta = self._lat_long_upper_left.long - lat_long_pair.long
        long_frac =  long_delta / long_span
        x = self._x_y_size[0] * long_frac

        # print(f" map_lat_long_to_x_y {lat_long_pair} -> {(x,y)}")

        return (int(x), int(y))

def test_1():

    # map a rect at lat,lon 50,120 - 45,125 to a 200x200 output

    ul = lat_long(50, -125)
    lr = lat_long(45, -120)
    m = mapper(ul, lr, (200, 200))

    # should be (0, 0)
    x = lat_long(50, -125)
    x2 = m.map_lat_long_to_x_y(x)
    print(f"{x} -> {x2}")

    # should be (200,200)
    x = lat_long(45, -120)
    x2 = m.map_lat_long_to_x_y(x)
    print(f"{x} -> {x2}")

    # should be (120,80)
    x = lat_long(48, -122)
    x2 = m.map_lat_long_to_x_y(x)
    print(f"{x} -> {x2}")

def test_2():

    # more realistic

    ul = lat_long(47.7, -122.5)
    lr = lat_long(47.5, -122.0)
    m = mapper(ul, lr, (200, 200))

    # should be (100,100)
    x = lat_long(47.6, -122.25)
    x2 = m.map_lat_long_to_x_y(x)
    print(f"{x} -> {x2}")


# test_1()
# test_2()
