import atexit
import json
import logging
import os
import subprocess
import tempfile
import time
from typing import Dict

import click
import orjson
import rapidjson
import tqdm
import ujson
from mimesis.schema import (
    Field,
    Schema,
)

SERIALIZERS = {
    'json': lambda obj: json.dumps(obj, separators=(',', ':')),
    'orjson': lambda obj: orjson.dumps(obj).decode('utf-8'),
    'rapidjson': rapidjson.dumps,
    'ujson': ujson.dumps,
}

_ = Field('en', seed=42)

log = logging.getLogger(__name__)


class BenchmarkMeta(type):
    REQUIRED_KEYS = {
        'version',
        'iterations',
        'schema',
    }

    def __new__(cls, name, bases, dct):
        new_cls = super().__new__(cls, name, bases, dct)

        if name != 'BaseBenchmark':
            for key in cls.REQUIRED_KEYS:
                if key not in dct:
                    raise NotImplementedError(f'Benchmark missing key: {key}')

            ALL_BENCHMARKS[name] = new_cls
        return new_cls


class BaseBenchmark(metaclass=BenchmarkMeta):
    # XXX: this is so auto-completion works
    version = None
    iteration = None
    schema = None

    @classmethod
    def cache_filename(cls, serializer):
        return f'{cls.__name__}.{cls.version}.{serializer}'


ALL_BENCHMARKS: Dict[str, BaseBenchmark] = {}


class Simple1Benchmark(BaseBenchmark):
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
        'str': _('text.sentence'),
        'datetime': _('datetime.formatted_datetime', fmt='%Y-%m-%dT%H:%M:%S %Z'),
        'coordinates': _('address.coordinates'),
        'null': None,
    }


@click.command()
@click.option('--benchmark', type=click.Choice(ALL_BENCHMARKS.keys()), required=True)
@click.option('--serializer', type=click.Choice(SERIALIZERS.keys()), default='json')
@click.option('--cache-dir', help='cache directory for serialized file')
@click.option('--only-serialize', is_flag=True, default=False, help='exit after serializing without running DESERIALIZER_CMD')
@click.argument('deserializer_cmd')
def main(benchmark, serializer, cache_dir, only_serialize, deserializer_cmd):
    """
    Runs a benchmark against a specific deserializer by serializing generated
    data with a schema defined by `--benchmark` and a serializer specified by
    `--serializer`.  Optionally may be run in validation mode with `--validate`
    which will ensure that the output by the deserializer matches the expected
    values (TODO).

    DESERIALIZER_CMD should be a string containing a command that takes two
    arguments, the name of the benchmark marked by the placeholder "$BENCHMARK"
    and the input filename marked by the placeholder "$FILENAME".  For example:

        "python json_deser.py $BENCHMARK $FILENAME"

    """
    benchmark_cls = ALL_BENCHMARKS[benchmark]
    schema = Schema(schema=benchmark_cls.schema)
    serializer_cls = SERIALIZERS[serializer]

    def setup_logging():
        logging.basicConfig(
            level=os.environ.get('LOG_LEVEL', logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def verify_deserialize_cmd():
        for placeholder in ('$BENCHMARK', '$FILENAME', ):
            if not only_serialize and placeholder not in deserializer_cmd:
                raise click.BadArgumentUsage(f'DESERIALIZER_CMD missing placeholder: {placeholder}')

    def print_preamble():
        log.info('Running benchmark: %s', benchmark)
        log.info('Using library for serialization: %s', serializer)
        if cache_dir:
            log.info('Using cache directory: %s', cache_dir)

    def get_serialized_filename() -> str:
        if not cache_dir:
            log.info('Not using cache_dir, test will generate a temporary file (use --cache-dir to speed up subsequent test runs)')
            serialized_filename = tempfile.mkstemp()[1]
            log.debug('Using temporary filename: %s', serialized_filename)
            atexit.register(os.remove, serialized_filename)
        else:
            serialized_filename = os.path.join(cache_dir, benchmark_cls.cache_filename(serializer))

        return serialized_filename

    def generate_serialized_file():
        if not os.path.exists(serialized_filename) or not os.path.getsize(serialized_filename):
            log.info('Writing serialized file to: %s', serialized_filename)
            start_time = time.time()

            with open(serialized_filename, 'w') as fp:
                for _ in tqdm.trange(benchmark_cls.iterations):
                    line = schema.create(iterations=1)[0]
                    fp.write(serializer_cls(line))
                    fp.write('\n')

            log.info(
                'Serializer time taken: %.2fs (%.2f lines/sec)',
                time.time() - start_time,
                benchmark_cls.iterations / (time.time() - start_time),
            )

    def run_deserialize_benchmark():
        start_time = time.time()
        cmd = deserializer_cmd.replace('$BENCHMARK', benchmark).replace('$FILENAME', serialized_filename)
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        count = 0
        with tqdm.tqdm(total=benchmark_cls.iterations) as progress:
            while True:
                buf = proc.stdout.read(4096)
                if not buf:
                    break

                count += buf.count(b'\n')
                progress.update(buf.count(b'\n'))

        if count != benchmark_cls.iterations:
            log.error('Expected %d lines, only got back %d', benchmark_cls.iterations, count)

        log.info(
            'Deserialize time taken: %.2fs (%.2f lines/sec)',
            time.time() - start_time,
            benchmark_cls.iterations / (time.time() - start_time),
        )

    setup_logging()
    verify_deserialize_cmd()
    print_preamble()
    serialized_filename = get_serialized_filename()
    generate_serialized_file()

    if only_serialize:
        raise SystemExit()

    run_deserialize_benchmark()
