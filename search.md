
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
```
class Filter(enabled=None, found=None, terrain=None, difficulty=None, 
personal_note=None, corrected_coordinates=None, premium=None)
```
## supported
* Terrain 
* Difficulty
* Cache status
* Personal Note
* Found status
* Corrected Coordinates
* Membership type

# membership

# 

## not supported
* Geocache types (and group of types)
* Geocache size
* Favorite points (int)
* Owner ship
* Hidden by
* Keyword
* Not found by
* Place Date (after, before, between, on)
* Limit to country or region (includes a enumeration of countries and regions)

  



        if minimum_favorite_points is not None:
            params['fav'] = str(int(minimum_favorite_points))

