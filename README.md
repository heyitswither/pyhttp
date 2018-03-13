# pyhttp
simple http client written in python

```
usage: pyhttp [-h] [-V] [-v] [-M METHOD] [-D DATA]
              [-H [HEADERS [HEADERS ...]]] [-R] [--no-default-headers]
              url

a non-interactive network retriever, written in Python

positional arguments:
  url                   URL to work with

optional arguments:
  -h, --help            show this help message and exit
  -V, --verbose         Make the operation more talkative
  -v, --version         Show the version number and quit
  -M METHOD, --method METHOD
                        Method used for HTTP request
  -D DATA, --data DATA  Data to send in request
  -H [HEADERS [HEADERS ...]], --headers [HEADERS [HEADERS ...]]
                        Send custom headers
  -R, --no-redirect     Don't ollow redirects
  --no-default-headers  Only send custom headers
```
