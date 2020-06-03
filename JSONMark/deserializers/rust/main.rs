use std::env;
use std::fs::File;
use std::io::{self, prelude::*, BufReader};
use simd_json;

fn main() -> io::Result<()>{
    let args: Vec<String> = env::args().collect();

    let _file = File::open(&args[2])?;
    let reader = BufReader::new(_file);

    for line in reader.split(b'\n') {
        let mut buf = line?;
        // XXX: slower serde_json
        // let v: Value = serde_json::from_slice(&mut buf)?;
        let v: simd_json::BorrowedValue = simd_json::to_borrowed_value(&mut buf).unwrap();
        print!("{}\n", v["integer_1"]);
    }

    return Ok(());
}
