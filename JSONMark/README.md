# JSONMark

## Usage

```
Usage: jsonmark [OPTIONS] DESERIALIZER_CMD

  Runs a benchmark against a specific deserializer by serializing generated
  data with a schema defined by `--benchmark` and a serializer specified by
  `--serializer`.  Optionally may be run in validation mode with
  `--validate` which will ensure that the output by the deserializer matches
  the expected values (TODO).

  DESERIALIZER_CMD should be a string containing a command that takes an
  argument, the input filename marked by the placeholder "$FILENAME". For
  example:

      "python json_deser.py $FILENAME"

Options:
  --benchmark [Simple1Benchmark]  [required]
  --serializer [json|orjson|rapidjson|ujson]
  --cache-dir TEXT                cache directory for serialized file
  --only-serialize                exit after serializing without running
                                  DESERIALIZER_CMD

  --profile                       profile memory/cpu usage
  --help                          Show this message and exit.
```

## Examples

Running JSONMark directly:

```
jsonmark --benchmark Simple1Benchmark 'python deserializers/python/main.py orjson $FILENAME'
```

Passing custom arguments via pre-defined deserializers in Makefile:

```
make python-orjson JSONMARK_COMMAND='jsonmark --profile --cache-dir cache --benchmark Simple1Benchmark'
```

## Results (2022-01-26)

Environment:

- AMD Ryzen 3950X
- Ubuntu 20.04 (Linux 5.4.0-90)
- Python: 3.10.1
- Node.js: v14.16.0
- Java: openjdk 11.0.13
- Rust: 1.47.0
- C++: clang version 10.0.0-4ubuntu1
- Go: go1.17

Tests:

- python: Various JSON libraries
- nodejs: Native JSON library
- java: java.io.BufferedReader + fastjson
- rust: simd_json
- cpp: simdjson using DOM and ondemand APIs
- go: encoding/json, segmentio/encoding/json, and buger/jsonparser

Observations:

- orjson was the winner for Python.
- Reading from a file in Java alone was taking ~0.6s.  Not sure if more work
  is occurring due to reading/decoding to a string (though we're only using
  ASCII in our test, and testing US-ASCII as the Charset made no difference).
  Other approaches to reading from a file were the same or worse.
- Rust simd_json is a port of an an older version of simdjson.  There are
  bindings to the C++ version but did not try.  Interestingly, serde_json
  performs very similarly to python-orjson (I would have expected a bit more
  overhead in Python).
- C++ simdjson was the winner overall.  The "dom-load-many" and "ondemand-load"
  are faster, but they read the entire file into memory first, but
  "cpp-dom-getline" still performance the best out of all iterative approaches.
- Go's standard JSON library is very slow.  Unmarshalling to a struct is faster
  than an unstructured interface, regardless of the library used.
  buger/jsonparser is not a fair comparison because it is only parsing a subset
  of keys that were specified, but it is still a decent choice if you don't
  need to parse all the keys.  When parsing all the keys explicitly, it was
  still just slightly faster than the structured version of
  segmentio/encoding/json.

|        benchmark         |time_1 (in sec)|time_2|time_3|time_avg|cpu (95th util %)|mem (95th MiB)|% time|
|--------------------------|--------------:|-----:|-----:|-------:|----------------:|-------------:|-----:|
|python-orjson             |           2.15|  2.15|  2.24|    2.18|           103.04|         14.55|100.00|
|python-json               |           6.68|  6.61|  6.52|    6.60|           105.70|         14.62|302.75|
|python-ujson              |           3.30|  3.30|  3.28|    3.29|           105.93|         14.69|150.92|
|python-rapidjson          |           4.44|  4.35|  4.37|    4.39|           103.33|         14.52|201.38|
|python-simdjson           |           2.79|  2.84|  2.87|    2.83|           104.08|         14.65|129.82|
|nodejs                    |           2.59|  2.59|  2.54|    2.57|           108.20|         54.42|117.89|
|java                      |           2.36|  2.46|  2.42|    2.41|           158.12|       1276.21|110.55|
|rust                      |           1.06|  1.05|  1.05|    1.05|           102.15|          2.61| 48.17|
|cpp-dom-getline           |           0.42|  0.42|  0.42|    0.42|            88.56|          2.11| 19.27|
|cpp-dom-load-many         |           0.38|  0.38|  0.39|    0.38|             0.00|        319.99| 17.43|
|cpp-ondemand-load         |           0.26|  0.27|  0.27|    0.27|             0.00|        320.00| 12.39|
|go-unstructured-json      |          12.20| 12.37| 12.36|   12.31|           113.88|          8.65|564.68|
|go-structured-json        |           6.97|  7.05|  7.02|    7.01|           111.33|          8.61|321.56|
|go-unstructured-siojson   |           7.16|  7.15|  7.15|    7.15|           128.42|          9.55|327.98|
|go-structured-siojson     |           2.13|  2.08|  2.03|    2.08|           110.70|          8.94| 95.41|
|go-unstructured-jsonparser|           0.36|  0.34|  0.32|    0.34|             0.00|          7.78| 15.60|
