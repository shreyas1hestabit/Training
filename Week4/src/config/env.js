import dotenv from "dotenv";
import path from "path";

const rootPath = path.resolve(process.cwd(),"..");
const env = process.env.NODE_ENV || "local";

dotenv.config({
  path: path.join(rootPath, `.env.${env}`)
});
