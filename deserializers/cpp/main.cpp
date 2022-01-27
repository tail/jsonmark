#include <iostream>
#include <map>
#include <stdio.h>
#include <stdlib.h>
#include "simdjson.h"

typedef void (*BenchmarkFunction)(char *);
static std::map<std::string, BenchmarkFunction> benchmarks;

void dom_getline(char *filename) {
    // XXX: Slightly slower version going line by line manually instead of
    // using `load_many`.
    FILE *stream;

    stream = fopen(filename, "r");
    if (stream == NULL) {
        perror("fopen");
        exit(EXIT_FAILURE);
    }

    size_t nread;
    size_t len;
    char *line = NULL;
    int64_t checksum = 0;
    simdjson::dom::parser parser;
    while ((nread = getline(&line, &len, stream)) != -1) {
        auto doc = parser.parse(line, nread);
        checksum += int64_t(doc["integer_1"]) + int64_t(doc["integer_2"]);
    }
    std::cout << checksum << std::endl;

    free(line);
    fclose(stream);
}

void dom_load_many(char *filename) {
    simdjson::dom::parser parser;
    int64_t checksum = 0;

    for (simdjson::dom::element doc : parser.load_many(filename)) {
        checksum += int64_t(doc["integer_1"]) + int64_t(doc["integer_2"]);
    }

    std::cout << checksum << std::endl;
}

void ondemand_load(char *filename) {
    simdjson::ondemand::parser parser;
    int64_t checksum = 0;

    simdjson::padded_string json = simdjson::padded_string::load(filename);
    simdjson::ondemand::document_stream docs = parser.iterate_many(json);

    for (auto doc : docs) {
        checksum += int64_t(doc["integer_1"]) + int64_t(doc["integer_2"]);
    }

    std::cout << checksum << std::endl;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        std::cout << "expected two args: <benchmark> <filename>" << std::endl;
        return 1;
    }

    benchmarks["dom_getline"] = dom_getline;
    benchmarks["dom_load_many"] = dom_load_many;
    benchmarks["ondemand_load"] = ondemand_load;

    if (benchmarks.count(argv[1])) {
        benchmarks[argv[1]](argv[2]);
    } else {
        std::cout << "benchmark not found: " << argv[1] << std::endl;
        return 1;
    }

    return 0;
}
