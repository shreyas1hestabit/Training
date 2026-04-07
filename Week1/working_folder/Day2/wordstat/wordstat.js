#!/usr/bin/env node

const fs = require("fs");
const { Worker } = require("worker_threads");
const path = require("path");


const args = process.argv.slice(2);
const params = {};

for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith("--")) {
    const key = args[i].replace("--", "");
    const val =
      args[i + 1] && !args[i + 1].startsWith("--") ? args[i + 1] : true;
    params[key] = val;
  }
}

if (!params.file) {
  console.error("ERROR: --file <path> must be provided");
  process.exit(1);
}

const FILE_PATH = params.file;
const TOP_N = parseInt(params.top || 10, 10);
const MIN_LEN = parseInt(params.minLen || 1, 10);
const UNIQUE_ONLY = !!params.unique;
const CONCURRENCY = parseInt(params.concurrency || 1, 10);


const OUTPUT_DIR = "output";
const LOG_DIR = "logs";
const STATS_FILE = path.join(OUTPUT_DIR, "stats.json");
const PERF_FILE = path.join(LOG_DIR, "perf-summary.json");


fs.mkdirSync(OUTPUT_DIR, { recursive: true });
fs.mkdirSync(LOG_DIR, { recursive: true });


const fileSize = fs.statSync(FILE_PATH).size;
const chunkSize = Math.ceil(fileSize / CONCURRENCY);

function createChunkRanges() {
  const ranges = [];
  for (let i = 0; i < CONCURRENCY; i++) {
    ranges.push({
      start: i * chunkSize,
      end: Math.min((i + 1) * chunkSize, fileSize),
    });
  }
  return ranges;
}


function runWorker(range) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(
      `
      const { parentPort, workerData } = require("worker_threads");
      const fs = require("fs");

      const { file, start, end, minLen, uniqueOnly } = workerData;

      const fd = fs.openSync(file, "r");
      const size = end - start;
      const buffer = Buffer.alloc(size);
      fs.readSync(fd, buffer, 0, size, start);

      let text = buffer.toString("utf8").replace(/\\n+/g, " ");

      const words = text.toLowerCase().match(/[a-zA-Z]+/g) || [];
      const filtered = words.filter(w => w.length >= minLen);

      const stats = {
        total: filtered.length,
        longest: "",
        shortest: filtered[0] || "",
        counts: {}
      };

      for (const w of filtered) {
        if (!stats.longest || w.length > stats.longest.length) stats.longest = w;
        if (!stats.shortest || w.length < stats.shortest.length) stats.shortest = w;

        if (!uniqueOnly) {
          stats.counts[w] = (stats.counts[w] || 0) + 1;
        }
      }

      parentPort.postMessage(stats);
    `,
      {
        eval: true,
        workerData: {
          file: FILE_PATH,
          ...range,
          minLen: MIN_LEN,
          uniqueOnly: UNIQUE_ONLY,
        },
      }
    );

    worker.on("message", resolve);
    worker.on("error", reject);
  });
}

(async () => {
  const startTime = process.hrtime.bigint();

  const ranges = createChunkRanges();
  const results = await Promise.all(ranges.map(runWorker));


  let totalWords = 0;
  let longest = "";
  let shortest = results[0]?.shortest || "";
  const globalCounts = {};

  for (const r of results) {
    totalWords += r.total;

    if (r.longest.length > longest.length) longest = r.longest;
    if (!shortest || (r.shortest && r.shortest.length < shortest.length))
      shortest = r.shortest;

    for (const [w, c] of Object.entries(r.counts)) {
      globalCounts[w] = (globalCounts[w] || 0) + c;
    }
  }

  const uniqueWords = Object.keys(globalCounts).length;

  const top = Object.entries(globalCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, TOP_N)
    .map(([word, count]) => ({ word, count }));


  const statsPayload = {
    file: FILE_PATH,
    concurrency: CONCURRENCY,
    minLength: MIN_LEN,
    topN: TOP_N,
    totals: {
      totalWords,
      uniqueWords,
    },
    extremes: {
      longestWord: longest,
      shortestWord: shortest,
    },
    topRepeatedWords: top,
  };

  fs.writeFileSync(STATS_FILE, JSON.stringify(statsPayload, null, 2));

  console.log("Stats written to:", STATS_FILE);


  const endTime = process.hrtime.bigint();
  const durationMs = Number(endTime - startTime) / 1_000_000;

  const perfEntry = {
    file: FILE_PATH,
    concurrency: CONCURRENCY,
    runtimeMs: Math.round(durationMs),
    timestamp: new Date().toISOString(),
  };


  let perfLog = [];
  if (fs.existsSync(PERF_FILE)) {
    try {
      perfLog = JSON.parse(fs.readFileSync(PERF_FILE, "utf8"));
    } catch {}
  }

  perfLog.push(perfEntry);
  fs.writeFileSync(PERF_FILE, JSON.stringify(perfLog, null, 2));

  console.log("Perf log updated:", PERF_FILE);


  console.log("\n--- RESULT SUMMARY ---");
  console.log("File:", FILE_PATH);
  console.log("Concurrency:", CONCURRENCY);
  console.log("Total words:", totalWords);
  console.log("Unique words:", uniqueWords);
  console.log("Longest word:", longest);
  console.log("Shortest word:", shortest);
  console.log(`Top ${TOP_N} words:`);
  top.forEach(t => console.log(`  ${t.word} = ${t.count}`));
})();

