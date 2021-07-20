# This code opens the url of the api endpoint and reads it to the variable source.
# Then using the module json, it converts the json object to python objects.

import json
from urllib.request import urlopen

API_endpoint = ''

with urlopen(API_endpoint) as response:
    source = response.read()

data = json.loads(source)

# print(json.dumps(data, indent=2))
