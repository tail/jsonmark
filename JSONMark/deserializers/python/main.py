import json
import sys

import orjson
import rapidjson
import simdjson
import ujson

DESERIALIZERS = {
    'json': lambda obj: json.loads(obj),
    'orjson': lambda obj: orjson.loads(obj),
    'rapidjson': rapidjson.loads,
    'simdjson': simdjson.loads,  # type: ignore
    'ujson': ujson.loads,
}


def main():
    serializer = sys.argv[1]
    benchmark = sys.argv[2]
    filename = sys.argv[3]

    if serializer not in DESERIALIZERS:
        print(f"Unknown serializer: {serializer}")
        sys.exit(1)

    loads = DESERIALIZERS[serializer]

    checksum = 1
    for line in open(filename, 'rb'):
        data = loads(line)
        checksum += data['integer_1'] + data['integer_2']
    print(checksum)

if __name__ == "__main__":
    main()
