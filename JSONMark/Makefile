.EXPORT_ALL_VARIABLES:
LOG_LEVEL = DEBUG

python-orjson:
	jsonmark --cache-dir cache --benchmark Simple1Benchmark 'python deserializers/python/main.py orjson $$FILENAME'

nodejs:
	jsonmark --cache-dir cache --benchmark Simple1Benchmark 'node deserializers/nodejs/main.js $$FILENAME'

deserializers/java/build/libs/jsonmark-deserializer-all.jar: deserializers/java/src/main/java/im/tail/jsonmark/deserializer/App.java
	cd deserializers/java && ./gradlew shadowJar

java: deserializers/java/build/libs/jsonmark-deserializer-all.jar
	jsonmark --cache-dir cache --benchmark Simple1Benchmark 'java -jar deserializers/java/build/libs/jsonmark-deserializer-all.jar $$FILENAME'

./deserializers/rust/target/release/jsonmark-deserializer-rust: deserializers/rust/main.rs
	cd deserializers/rust && cargo build --release

rust: ./deserializers/rust/target/release/jsonmark-deserializer-rust
	jsonmark --cache-dir cache --benchmark Simple1Benchmark './deserializers/rust/target/release/jsonmark-deserializer-rust $$FILENAME'

export CC=clang
export CXX=clang++
./deserializers/cpp/build: ./deserializers/cpp/meson.build
	cd deserializers/cpp && meson build --optimization=3 || meson --reconfigure build

./deserializers/cpp/build/main: ./deserializers/cpp/main.cpp ./deserializers/cpp/build
	cd deserializers/cpp/build && ninja

cpp-dom-getline: ./deserializers/cpp/build/main
	jsonmark --cache-dir cache --benchmark Simple1Benchmark './deserializers/cpp/build/main dom_getline $$FILENAME'

cpp-dom-load-many: ./deserializers/cpp/build/main
	jsonmark --cache-dir cache --benchmark Simple1Benchmark './deserializers/cpp/build/main dom_load_many $$FILENAME'

cpp-ondemand-load: ./deserializers/cpp/build/main
	jsonmark --cache-dir cache --benchmark Simple1Benchmark './deserializers/cpp/build/main ondemand_load $$FILENAME'

./deserializers/go/main: ./deserializers/go/main.go
	cd deserializers/go && go build -o main

go-unstructured-json: ./deserializers/go/main
	jsonmark --cache-dir cache --benchmark Simple1Benchmark './deserializers/go/main UnstructuredJSON $$FILENAME'

go-structured-json: ./deserializers/go/main
	jsonmark --cache-dir cache --benchmark Simple1Benchmark './deserializers/go/main StructuredJSON $$FILENAME'

go-unstructured-siojson: ./deserializers/go/main
	jsonmark --cache-dir cache --benchmark Simple1Benchmark './deserializers/go/main UnstructuredSIOJSON $$FILENAME'

go-structured-siojson: ./deserializers/go/main
	jsonmark --cache-dir cache --benchmark Simple1Benchmark './deserializers/go/main StructuredSIOJSON $$FILENAME'

go-unstructured-jsonparser: ./deserializers/go/main
	jsonmark --cache-dir cache --benchmark Simple1Benchmark './deserializers/go/main UnstructuredJSONParser $$FILENAME'

clean:
	rm -rf deserializers/cpp/build
	rm -rf deserializers/java/build
	rm -rf deserializers/rust/target
