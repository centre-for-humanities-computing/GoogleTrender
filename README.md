# GoogleTrender
Uses the pytrends api to fetch trends and then allows the comparison among a large (theoretically infinite) amount of keywords.

## Usage:
Start by installing requirements.txt
```python
pip3 install -r requirements.txt
```

Trender.py usage:
```python
Usage: Trender.py [options]

Options:
  -h, --help            show this help message and exit
  -i INPUT, --terms=INPUT
                        txt file with newline separated search terms
  -d DATERANGE, --daterange=DATERANGE
                        The range of dates for which to fetch trend data
  -l GEO, --locality=GEO
                        2 letter locale from whence to fetch the data.
  -e, --interactive     output interactive plot in browser
  -o OUTPUT, --output=OUTPUT
                        output path for plot
```

The daterange format can be gathered from the original [pytrends](https://github.com/GeneralMills/pytrends) package.

## Future work:
* Interactive and static plots. At present time only interactive plots are active.
* Make into a package

