use std::env;
use std::fs::File;
use std::io::{self, prelude::*, BufReader};
use simd_json;
use simd_json::Value;
// use serde_json;
// use serde_json::Value;

fn main() -> io::Result<()>{
    let args: Vec<String> = env::args().collect();

    let _file = File::open(&args[1])?;
    let reader = BufReader::new(_file);

    let mut checksum = 0;
    for line in reader.split(b'\n') {
        let mut buf = line?;
        // XXX: slower serde_json
        // let v: Value = serde_json::from_slice(&mut buf)?;
        let v: simd_json::BorrowedValue = simd_json::to_borrowed_value(&mut buf).unwrap();
        checksum += v["integer_1"].as_i64().unwrap();
        checksum += v["integer_2"].as_i64().unwrap();
    }
    print!("{}\n", checksum);

    return Ok(());
}
