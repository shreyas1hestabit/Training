const fs = require("fs");

console.time("Stream Read Time");


const startMemory = process.memoryUsage().rss;

let totalBytes = 0;

const stream = fs.createReadStream("textfile.txt", {
  highWaterMark: 1024 * 1024
});

stream.on("data", chunk => {
  totalBytes += chunk.length;


});

stream.on("end", () => {
  const endMemory = process.memoryUsage().rss;

  console.timeEnd("Stream Read Time");

  console.log("\nTotal bytes read:", totalBytes);

  console.log("\nMemory Usage (MB):");
  console.log("Before:", (startMemory / 1024 / 1024).toFixed(2));
  console.log("After :", (endMemory / 1024 / 1024).toFixed(2));
  console.log(
    "Difference:",
    ((endMemory - startMemory) / 1024 / 1024).toFixed(2),
    "MB"
  );
});

stream.on("error", err => {
  console.error("Stream error:", err);
});
