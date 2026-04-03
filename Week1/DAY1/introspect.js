const os = require("os");
const { execSync } = require("child_process");

function formatUptime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${h}h ${m}m ${s}s`;
}
function getLoggedUser() {
  try {
    return os.userInfo().username;
  } catch {
    try {
      return execSync("whoami").toString().trim();
    } catch {
      return "Unknown";
    }
  }
}

console.log("OS:", `${os.type()} ${os.release()}`);
console.log("Architecture:", os.arch());
console.log("CPU Cores:", os.cpus().length);
console.log("Total Memory:", `${(os.totalmem() / 1024 / 1024 / 1024).toFixed(2)} GB`);
console.log("System Uptime:", formatUptime(os.uptime()));
console.log("Current Logged User:", getLoggedUser());
console.log("Node Path:", process.execPath);
