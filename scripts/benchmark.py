#!/usr/bin/env python3
import os
import re
import subprocess

import numpy as np
from pytablewriter import MarkdownTableWriter  # type: ignore

ITERATIONS = 3

TABLE_HEADER = ["benchmark", "time_1 (in sec)", "time_2", "time_3", "time_avg", "cpu (95th util %)", "mem (95th MiB)", "% time"]
COL_TIME_AVG = 4

RE_TIME_TAKEN = re.compile(r"time taken: (\d+\.\d+)s")
RE_CPU_95TH = re.compile(r"CPU.*95%=(\d+\.\d+)")
RE_MEM_95TH = re.compile(r"MEM.*95%=(\d+\.\d+)")

JSONMARK_COMMAND = "JSONMARK_COMMAND='jsonmark --cache-dir cache --benchmark Simple1Benchmark'"
JSONMARK_COMMAND_PROFILE = "JSONMARK_COMMAND='jsonmark --profile --cache-dir cache --benchmark Simple1Benchmark'"

# XXX: first benchmark is used as baseline for all other tests
BENCHMARKS = [
    "python-orjson",
    "python-json",
    "python-ujson",
    "python-rapidjson",
    "python-simdjson",
    "nodejs",
    "java",
    "rust",
    "cpp-dom-getline",
    "cpp-dom-load-many",
    "cpp-ondemand-load",
    "go-unstructured-json",
    "go-structured-json",
    "go-unstructured-siojson",
    "go-structured-siojson",
    "go-unstructured-jsonparser",
    "go-unstructured-ast-sonic",
    "go-unstructured-map-sonic",
    "go-structured-sonic",
]


def format_float(num) -> str:
    return "%.2f" % (num, )

def run_benchmark(benchmark, command) -> bytes:
    return subprocess.check_output(
        [f"make {command} {benchmark}"],
        shell=True,
        stderr=subprocess.STDOUT,
        cwd=os.path.join(os.path.dirname(__file__), os.pardir),
    )


def main():
    rows = []

    for counter, benchmark in enumerate(BENCHMARKS):
        row = [benchmark]

        # get test runs and average
        for i in range(ITERATIONS):
            print(f"Running '{benchmark}' {i + 1} of {ITERATIONS}")
            output = run_benchmark(benchmark, JSONMARK_COMMAND)
            time_taken_match = RE_TIME_TAKEN.search(output.decode("utf-8"))
            if not time_taken_match:
                raise ValueError(f"could not find 'time taken' from output: {output}")

            row.append(time_taken_match.group(1))

        row.append(
            format_float(
                np.average([float(x) for x in row[1:ITERATIONS + 1]])  # type: ignore
            )
        )

        print(f"Running '{benchmark}' with --profile")
        # get cpu/mem
        output = run_benchmark(benchmark, JSONMARK_COMMAND_PROFILE).decode("utf-8")
        cpu_95th_match = RE_CPU_95TH.search(output)
        if not cpu_95th_match:
            raise ValueError(f"could not find 'cpu 95th' from output: {output}")
        row.append(cpu_95th_match.group(1))

        mem_95th_match = RE_MEM_95TH.search(output)
        if not mem_95th_match:
            raise ValueError(f"could not find 'mem 95th' from output: {output}")
        row.append(mem_95th_match.group(1))

        # add % of baseline time.  if this is the first iteration, it's just 100%
        if counter == 0:
            row.append("100.00")
        else:
            row.append(format_float(100.0 * float(row[COL_TIME_AVG]) / float(rows[0][COL_TIME_AVG])))

        print(row)

        rows.append(row)

    writer = MarkdownTableWriter(
        table_name="Results",
        headers=TABLE_HEADER,
        value_matrix=rows
    )

    writer.write_table()


if __name__ == "__main__":
    main()
