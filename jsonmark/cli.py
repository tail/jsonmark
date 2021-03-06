import atexit
import json
import logging
import os
import subprocess
import tempfile
import time

import click
import numpy as np
import orjson
import rapidjson
import tqdm
import ujson
from mimesis.schema import Schema
from rich.console import Console

from jsonmark.benchmarks import ALL_BENCHMARKS

SERIALIZERS = {
    'json': lambda obj: json.dumps(obj, separators=(',', ':')),
    'orjson': lambda obj: orjson.dumps(obj).decode('utf-8'),
    'rapidjson': rapidjson.dumps,
    'ujson': ujson.dumps,
}

log = logging.getLogger(__name__)

console = Console()


@click.command()
@click.option('--benchmark', type=click.Choice(ALL_BENCHMARKS.keys()), required=True)
@click.option('--serializer', type=click.Choice(SERIALIZERS.keys()), default='json')
@click.option('--cache-dir', help='cache directory for serialized file')
@click.option('--only-serialize', is_flag=True, default=False, help='exit after serializing without running DESERIALIZER_CMD')
@click.option('--profile', is_flag=True, default=False, help='profile memory/cpu usage')
@click.argument('deserializer_cmd')
def main(benchmark, serializer, cache_dir, only_serialize, profile, deserializer_cmd):
    """
    Runs a benchmark against a specific deserializer by serializing generated
    data with a schema defined by `--benchmark` and a serializer specified by
    `--serializer`.  Optionally may be run in validation mode with `--validate`
    which will ensure that the output by the deserializer matches the expected
    values (TODO).

    DESERIALIZER_CMD should be a string containing a command that takes an
    argument, the input filename marked by the placeholder "$FILENAME".
    For example:

        "python json_deser.py $FILENAME"

    """
    benchmark_cls = ALL_BENCHMARKS[benchmark]
    schema = Schema(schema=benchmark_cls.schema)
    serializer_cls = SERIALIZERS[serializer]
    profile_filename = ''
    if profile:
        profile_filename = tempfile.mkstemp()[1]
        atexit.register(os.remove, profile_filename)

    def setup_logging():
        logging.basicConfig(
            level=os.environ.get('LOG_LEVEL', logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def verify_deserialize_cmd():
        for placeholder in ('$FILENAME', ):
            if not only_serialize and placeholder not in deserializer_cmd:
                raise click.BadArgumentUsage(f'DESERIALIZER_CMD missing placeholder: {placeholder}')

    def print_preamble():
        log.info('Running benchmark: %s', benchmark)
        log.info('Using library for serialization: %s', serializer)
        if cache_dir:
            log.info('Using cache directory: %s', cache_dir)
            os.makedirs(cache_dir, exist_ok=True)

    def get_serialized_filename() -> str:
        if not cache_dir:
            log.info('Not using cache_dir, test will generate a temporary file (use --cache-dir to speed up subsequent test runs)')
            serialized_filename = tempfile.mkstemp()[1]
            log.debug('Using temporary filename: %s', serialized_filename)
            atexit.register(os.remove, serialized_filename)
        else:
            serialized_filename = os.path.join(cache_dir, benchmark_cls.cache_filename(serializer))

        return serialized_filename

    def generate_serialized_file(serialized_filename: str):
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
        cmd = deserializer_cmd.replace('$FILENAME', serialized_filename)
        if profile:
            cmd = f"psrecord --log {profile_filename} --include-children '{cmd}'"

        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

        checksum = 0
        with console.status("") as status:
            while True:
                status.update(status="%.2fs" % (time.time() - start_time))
                if proc.poll() is not None:
                    if proc.stdout:
                        data = proc.stdout.read().strip()
                        try:
                            if profile:
                                data = data.split()[0]
                            checksum = int(data)
                        except ValueError:
                            log.error('Expected checksum from output. Standard output to follow')
                            log.error(data)
                    break

        # XXX: this is really slow for stdout from rust/java/c++... but no
        # impact on python.  something to do with buffering.  for now, not
        # handling stdout.
        #
        # proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        # count = 0
        # with tqdm.tqdm(total=benchmark_cls.iterations) as progress:
        #     while True:
        #         buf = proc.stdout.read(4096)

        #         count += buf.count(b'\n')
        #         progress.update(buf.count(b'\n'))

        #         if proc.poll() is not None:
        #             break

        if checksum != benchmark_cls.expected_checksum:
            log.error('Expected checksum %d but got back %d', benchmark_cls.expected_checksum, checksum)

        log.info(
            'Deserialize time taken: %.2fs (%.2f lines/sec)',
            time.time() - start_time,
            10 * benchmark_cls.iterations / (time.time() - start_time),
        )

    def parse_profile():
        cpu, mem = np.loadtxt(profile_filename, skiprows=1, usecols=(1, 2), unpack=True)
        log.info("CPU (%%)  : max=%.2f  50%%=%.2f  95%%=%.2f", np.max(cpu), np.median(cpu), np.quantile(cpu, 0.95))
        log.info("MEM (MiB): max=%.2f  50%%=%.2f  95%%=%.2f", np.median(mem), np.max(mem), np.quantile(mem, 0.95))

    setup_logging()
    verify_deserialize_cmd()
    print_preamble()
    serialized_filename = get_serialized_filename()
    generate_serialized_file(serialized_filename)

    if only_serialize:
        raise SystemExit()

    run_deserialize_benchmark()

    if profile:
        parse_profile()
