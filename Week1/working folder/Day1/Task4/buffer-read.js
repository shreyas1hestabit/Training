const fs = require("fs");

console.time("Buffer Read Time");


const startMemory = process.memoryUsage().rss;

const buffer = fs.readFileSync("textfile.txt");

const endMemory = process.memoryUsage().rss;

console.timeEnd("Buffer Read Time");

console.log("\nFile size (bytes):", buffer.length);

console.log("\nMemory Usage (MB):");
console.log("Before:", (startMemory / 1024 / 1024).toFixed(2));
console.log("After :", (endMemory / 1024 / 1024).toFixed(2));
console.log("Difference:", ((endMemory - startMemory) / 1024 / 1024).toFixed(2), "MB");
const preview = buffer.toString("utf8", 0, 200);
console.log("\nPreview:");
console.log(preview);

