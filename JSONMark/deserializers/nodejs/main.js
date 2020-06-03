const fs = require('fs');
const process = require('process');
const readline = require('readline');

const stream = fs.createReadStream(process.argv[3]);
const rl = readline.createInterface({
    input: stream,
    crlfDelay: Infinity,
});

rl.on('line', (line) => {
    console.log(JSON.parse(line).integer_1);
});
