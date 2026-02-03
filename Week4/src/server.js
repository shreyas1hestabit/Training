import "./config/env.js";
import { createApp } from "./loaders/app.js";

const app = await createApp();



app.listen(3000, () => {
  console.log("Server running on port 3000");
});
