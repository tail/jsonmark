from typing import Any, Callable, Dict

from mimesis.schema import Field

_ = Field('en', seed=42)


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

            ALL_BENCHMARKS[name] = new_cls  # type: ignore
        return new_cls


class BaseBenchmark(metaclass=BenchmarkMeta):
    version: int
    iterations: int
    schema: Callable[[], Dict[str, Any]]
    expected_checksum: int

    @classmethod
    def cache_filename(cls, serializer):
        return f'{cls.__name__}.{cls.version}.{serializer}'


ALL_BENCHMARKS: Dict[str, BaseBenchmark] = {}


class Simple1Benchmark(BaseBenchmark):
    version = 1
    seed = 42
    iterations = 1_000_000
    expected_checksum = -969896  # sum of integer_1 and integer_2
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
