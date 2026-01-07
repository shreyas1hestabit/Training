const fs = require("fs");

const FILE_PATH = "textfile.txt";

function toMB(bytes) {
  return (bytes / 1024 / 1024).toFixed(2);
}


function readWithBuffer() {
  const startMem = process.memoryUsage().rss;
  const startTime = process.hrtime.bigint();

  const data = fs.readFileSync(FILE_PATH);

  const endTime = process.hrtime.bigint();
  const endMem = process.memoryUsage().rss;

  return {
    executionTime: Number(endTime - startTime) / 1e6,
    memoryUsage: Number(endMem - startMem),
    bytesRead: data.length
  };
}


function readWithStream() {
  return new Promise(resolve => {
    const startMem = process.memoryUsage().rss;
    const startTime = process.hrtime.bigint();

    let totalBytes = 0;

    const stream = fs.createReadStream(FILE_PATH, {
      highWaterMark: 1024 * 1024
    });

    stream.on("data", chunk => {
      totalBytes += chunk.length;
    });

    stream.on("end", () => {
      const endTime = process.hrtime.bigint();
      const endMem = process.memoryUsage().rss;

      resolve({
        executionTime: Number(endTime - startTime) / 1e6,
        memoryUsage: Number(endMem - startMem),
        bytesRead: totalBytes
      });
    });

    stream.on("error", err => {
      console.error("Stream error:", err);
    });
  });
}




(async () => {
  console.log("Running buffer test...");
  const bufferResult = readWithBuffer();

  console.log("Running stream test...");
  const streamResult = await readWithStream();

  const results = {
    buffer: {
      executionTime_ms: bufferResult.executionTime.toFixed(3),
      memoryUsage_MB: toMB(bufferResult.memoryUsage),
      bytesRead: bufferResult.bytesRead
    },
    stream: {
      executionTime_ms: streamResult.executionTime.toFixed(3),
      memoryUsage_MB: toMB(streamResult.memoryUsage),
      bytesRead: streamResult.bytesRead
    }
  };


  const dir = "logs";
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir);
  }

  const outputPath = "logs/day1-perf.json";

  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));

  console.log(`\nSaved results to ${outputPath}`);
})();

