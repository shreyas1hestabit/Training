import express from "express";
import { createApp } from "./loaders/app.js";

const app = express();

await createApp(app);

app.listen(3000, () => {
  console.log("Server running on port 3000");
});
