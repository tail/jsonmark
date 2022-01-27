const fs = require('fs');
const process = require('process');
const readline = require('readline');

const stream = fs.createReadStream(process.argv[2]);
const rl = readline.createInterface({
    input: stream,
    crlfDelay: Infinity,
});

let checksum = 0;
rl.on('line', (line) => {
    const data = JSON.parse(line);
    checksum += data.integer_1 + data.integer_2;
});

rl.on('close', () => {
    console.log(checksum);
});
