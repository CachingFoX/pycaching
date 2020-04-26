
# Old search
```
geocaching = pycaching.login()
results = geocaching.search(Point(38.5314833, -28.63125), limit=150)
for item in results:
    print(item, item.size)
```

# Advanced search
## Without location
(from the home coordinates)
```
geocaching = pycaching.login()
results = geocaching.search_advanced(limit=150)
for item in results:
    print(item, item.size)
```

## With location
```
geocaching = pycaching.login()
results = geocaching.search_advanced(Point(38.5314833, -28.63125), limit=150)
for item in results:
    print(item, item.size)
```

## Home location
```
geocaching = pycaching.login()
results = geocaching.search_advanced('home', limit=150)
for item in results:
    print(item, item.size)
```

## Radius
Radius in Kilometer (km)
TODO: support miles (mi)


# Parameters
## supported
* Terrain 
* Difficulty
* Cache status
* Personal Note
* Found status

## not supported
* Geocache types (and group of types)
* Worldwide or origin with radius
* Geocache size
* Membership type
* Corrected Coordinates

* Favorite points
* Owner ship
* Hidden by
* Keyword
* Not found by
* Place Date (after, before, between, on)
* Limit to country or region (includes a enumeration of countries and regions)

        if premium is not None:
            params['p'] = '1' if enabled else '2'

        if updated_coordinates is not None:
            params['cc'] = '1' if updated_coordinates else '2'

        if minimum_favorite_points is not None:
            params['fav'] = str(int(minimum_favorite_points))

        if personal_note is not None:
            params['note'] = '1' if personal_note else '2'
