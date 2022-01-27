package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/buger/jsonparser"
	"github.com/minio/simdjson-go"
	siojson "github.com/segmentio/encoding/json"
)

type Simple struct {
	Integer1    int      `json:"integer_1"`
	Integer2    int      `json:"integer_2"`
	Float1      float64  `json:"float_1"`
	Float2      float64  `json:"float_2"`
	Bool        bool     `json:"bool"`
	Words       []string `json:"words"`
	Str         string   `json:"str"`
	Datetime    string   `json:"datetime"`
	Coordinates struct {
		Longitude float64 `json:"longitude"`
		Latitude  float64 `json:"latitude"`
	} `json:"coordinates"`
	Null interface{} `json:"null"`
}

type BenchmarkFunc func(data []byte) int

var Benchmarks = map[string]BenchmarkFunc{
	"UnstructuredJSON": UnstructuredJSON,
	"StructuredJSON":   StructuredJSON,

	"UnstructuredSIOJSON": UnstructuredSIOJSON,
	"StructuredSIOJSON":   StructuredSIOJSON,

	"UnstructuredJSONParser": UnstructuredJSONParser,

	"UnstructuredSIMDJSONParser": UnstructuredSIMDJSONParser,
}

func main() {
	if len(os.Args) != 3 {
		fmt.Printf("usage: %s <benchmark> <filename>\n", os.Args[0])
		os.Exit(1)
	}

	benchmark := os.Args[1]
	filename := os.Args[2]

	f, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}

	benchmarkFunc, ok := Benchmarks[benchmark]
	if !ok {
		fmt.Printf("Unknown benchmark function: %s\n", benchmark)
		os.Exit(1)
	}

	scanner := bufio.NewScanner(f)
	var checksum int = 0

	for scanner.Scan() {
		checksum += benchmarkFunc(scanner.Bytes())
	}

	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}

	fmt.Println(checksum)
}

func UnstructuredJSON(data []byte) int {
	var result map[string]interface{}
	if err := json.Unmarshal(data, &result); err != nil {
		log.Fatal(err)
	}
	// XXX: reflection parses integers as float64.  we're using an integer for
	// checksums, but the conversion from float64 -> int is negligible.
	return int(result["integer_1"].(float64) + result["integer_2"].(float64))
}

func UnstructuredSIOJSON(data []byte) int {
	var result map[string]interface{}
	if err := siojson.Unmarshal(data, &result); err != nil {
		log.Fatal(err)
	}
	return int(result["integer_1"].(float64) + result["integer_2"].(float64))
}

func StructuredJSON(data []byte) int {
	var result Simple
	if err := json.Unmarshal(data, &result); err != nil {
		log.Fatal(err)
	}
	return result.Integer1 + result.Integer2
}

func StructuredSIOJSON(data []byte) int {
	var result Simple
	if err := siojson.Unmarshal(data, &result); err != nil {
		log.Fatal(err)
	}
	return result.Integer1 + result.Integer2
}

// UnstructuredJSONParser is not a fair representation of JSON parsing as it
// will only attempt to parse the keys you request (see paths).
func UnstructuredJSONParser(data []byte) int {
	paths := [][]string{
		{"integer_1"},
		{"integer_2"},
		// XXX: uncommenting the rest of the keys will make this slower
		// {"float_1"},
		// {"float_2"},
		// {"bool"},
		// {"words"},
		// {"str"},
		// {"datetime"},
		// {"coordinates", "longitude"},
		// {"coordinates", "latitude"},
		// {"null"},
	}
	var int1 int64
	var int2 int64
	jsonparser.EachKey(data, func(idx int, value []byte, vt jsonparser.ValueType, err error) {
		switch idx {
		case 0:
			int1, _ = jsonparser.ParseInt(value)
		case 1:
			int2, _ = jsonparser.ParseInt(value)
		}
	}, paths...)

	return int(int1 + int2)
}

func UnstructuredSIMDJSONParser(data []byte) int {
	// TODO: this is extremely slow... probably doing something very wrong here
	pj, err := simdjson.Parse(data, nil)
	if err != nil {
		log.Fatal(err)
	}

	var elem *simdjson.Element
	var int1 int64
	var int2 int64

	_ = pj.ForEach(func(i simdjson.Iter) error {
		elem, err := i.FindElement(elem, "integer_1")
		if err == nil {
			int1, _ = elem.Iter.Int()
		}

		elem, err = i.FindElement(elem, "integer_2")
		if err == nil {
			int2, _ = elem.Iter.Int()
		}

		return nil
	})

	return int(int1 + int2)
}
