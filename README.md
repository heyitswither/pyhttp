# pyhttp
a non-interactive network retriever, written in Python

```
usage: pyhttp [-h] [-V] [-v] [-M METHOD] [-D DATA]
              [-H [HEADERS [HEADERS ...]]] [-R] [-A AUTH]
              [--no-default-headers]
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
  -A AUTH, --auth AUTH  Authenticate with the server(Type/User:Pass)
  --no-default-headers  Only send custom headers

```
