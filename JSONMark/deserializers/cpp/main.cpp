#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include "simdjson.h"

int main(int argc, char **argv) {
    if (argc != 3) {
        std::cout << "expected two args: <benchmark> <filename>" << std::endl;
        return 1;
    }

    // XXX: Slightly slower version going line by line manually instead of
    // using `load_many`.
    /*
    FILE *stream;

    stream = fopen(argv[2], "r");
    if (stream == NULL) {
        perror("fopen");
        exit(EXIT_FAILURE);
    }

    size_t nread;
    size_t len;
    char *line = NULL;
    simdjson::dom::parser parser;
    while ((nread = getline(&line, &len, stream)) != -1) {
        auto [doc, error] = parser.parse(line, nread);
        std::cout << doc["integer_1"] << std::endl;
    }

    free(line);
    fclose(stream);
    */

    simdjson::dom::parser parser;
    for (simdjson::dom::element doc : parser.load_many(argv[2])) {
        std::cout << doc["integer_1"] << std::endl;
    }

    return 0;
}
