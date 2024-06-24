from utils.encoder import BoilerPlateEncoder

import json


def pprint(data):
    print(json.dumps(data, cls=BoilerPlateEncoder, indent=2))


def pdump(data):
    return json.dumps(data, cls=BoilerPlateEncoder, indent=2)
