import json
import time

import click
import orjson
import rapidjson
import tqdm
import ujson
from mimesis.schema import (
    Field,
    Schema,
)

JSON_SERIALIZERS = {
    'json': lambda obj: json.dumps(obj,  separators=(',', ':')),
    'orjson': lambda obj: orjson.dumps(obj).decode('utf-8'),
    'rapidjson': rapidjson.dumps,
    'ujson': ujson.dumps,
}

_ = Field('en', seed=42)


class Simple1Benchmark:
    version = 1
    seed = 42
    iterations = 1_000_000
    schema = lambda: {
        'integer_1': _('numbers.integer_number'),
        'integer_2': _('numbers.integer_number'),
        'float_1': _('numbers.float_number'),
        'float_2': _('numbers.float_number'),
        'bool': _('development.boolean'),
        'words': _('text.words'),
        'str': _('text.sentence', ),
        'datetime': _('datetime.formatted_datetime', fmt='%Y-%m-%dT%H:%M:%S %Z'),
        'coordinates': _('address.coordinates'),
        'null': None,
    }


@click.command()
@click.option('--json-serializer', type=click.Choice(JSON_SERIALIZERS.keys()), default='json')
def main(json_serializer):
    print('Using JSON library for serialization:', json_serializer)

    benchmark = Simple1Benchmark
    schema = Schema(schema=benchmark.schema)
    json_serializer = JSON_SERIALIZERS[json_serializer]

    start_time = time.time()

    for _ in tqdm.trange(benchmark.iterations):
        line = schema.create(iterations=1)
        json_serializer(line)

    print('Time taken: %.2fs (%.2f lines/sec)' % (
        time.time() - start_time,
        1e6 / (time.time() - start_time),
    ))


if __name__ == '__main__':
    main()
