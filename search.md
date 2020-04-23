
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
