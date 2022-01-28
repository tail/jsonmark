JSONMARK_COMMAND ?= jsonmark --cache-dir cache --benchmark Simple1Benchmark
.EXPORT_ALL_VARIABLES:
LOG_LEVEL = DEBUG

python-orjson:
	$(JSONMARK_COMMAND) 'python deserializers/python/main.py orjson $$FILENAME'

python-json:
	$(JSONMARK_COMMAND) 'python deserializers/python/main.py json $$FILENAME'

python-ujson:
	$(JSONMARK_COMMAND) 'python deserializers/python/main.py ujson $$FILENAME'

python-rapidjson:
	$(JSONMARK_COMMAND) 'python deserializers/python/main.py rapidjson $$FILENAME'

python-simdjson:
	$(JSONMARK_COMMAND) 'python deserializers/python/main.py simdjson $$FILENAME'

nodejs:
	$(JSONMARK_COMMAND) 'node deserializers/nodejs/main.js $$FILENAME'

deserializers/java/build/libs/jsonmark-deserializer-all.jar: deserializers/java/src/main/java/im/tail/jsonmark/deserializer/App.java
	cd deserializers/java && ./gradlew shadowJar

java: deserializers/java/build/libs/jsonmark-deserializer-all.jar
	$(JSONMARK_COMMAND) 'java -jar deserializers/java/build/libs/jsonmark-deserializer-all.jar $$FILENAME'

./deserializers/rust/target/release/jsonmark-deserializer-rust: deserializers/rust/main.rs
	cd deserializers/rust && cargo build --release

rust: ./deserializers/rust/target/release/jsonmark-deserializer-rust
	$(JSONMARK_COMMAND) './deserializers/rust/target/release/jsonmark-deserializer-rust $$FILENAME'

export CC=clang
export CXX=clang++
./deserializers/cpp/build: ./deserializers/cpp/meson.build
	cd deserializers/cpp && meson build --optimization=3 || meson --reconfigure build

./deserializers/cpp/build/main: ./deserializers/cpp/main.cpp ./deserializers/cpp/build
	cd deserializers/cpp/build && ninja

cpp-dom-getline: ./deserializers/cpp/build/main
	$(JSONMARK_COMMAND) './deserializers/cpp/build/main dom_getline $$FILENAME'

cpp-dom-load-many: ./deserializers/cpp/build/main
	$(JSONMARK_COMMAND) './deserializers/cpp/build/main dom_load_many $$FILENAME'

cpp-ondemand-load: ./deserializers/cpp/build/main
	$(JSONMARK_COMMAND) './deserializers/cpp/build/main ondemand_load $$FILENAME'

./deserializers/go/main: ./deserializers/go/main.go
	cd deserializers/go && go build -o main

go-unstructured-json: ./deserializers/go/main
	$(JSONMARK_COMMAND) './deserializers/go/main UnstructuredJSON $$FILENAME'

go-structured-json: ./deserializers/go/main
	$(JSONMARK_COMMAND) './deserializers/go/main StructuredJSON $$FILENAME'

go-unstructured-siojson: ./deserializers/go/main
	$(JSONMARK_COMMAND) './deserializers/go/main UnstructuredSIOJSON $$FILENAME'

go-structured-siojson: ./deserializers/go/main
	$(JSONMARK_COMMAND) './deserializers/go/main StructuredSIOJSON $$FILENAME'

go-unstructured-jsonparser: ./deserializers/go/main
	$(JSONMARK_COMMAND) './deserializers/go/main UnstructuredJSONParser $$FILENAME'

go-unstructured-ast-sonic: ./deserializers/go/main
	$(JSONMARK_COMMAND) './deserializers/go/main UnstructuredASTSonic $$FILENAME'

go-unstructured-map-sonic: ./deserializers/go/main
	$(JSONMARK_COMMAND) './deserializers/go/main UnstructuredMapSonic $$FILENAME'

go-structured-sonic: ./deserializers/go/main
	$(JSONMARK_COMMAND) './deserializers/go/main StructuredSonic $$FILENAME'

clean:
	rm -rf deserializers/cpp/build
	rm -rf deserializers/java/build
	rm -rf deserializers/rust/target
