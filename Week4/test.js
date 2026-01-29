//yeh hamre port ko test krne k liye hai. basically hmara code chl bh rha hai ya nh woh chekc krne k liye ek temporary js file.
//import { config } from "./src/config/index.js"; //hm yha woh file with its config import krate hai jiski working hme check krni hai.
//console.log(config);

//to test the working of logger.js
// import {config} from "./src/config/index.js";
// import logger from "./src/utils/logger.js";
// logger.info("Logger is working");
// console.log(config);

//now we will test working of db.js
// import {config} from "./src/config/index.js";
// import logger from "./src/utils/logger.js";
// import {connectDB} from "./src/loaders/db.js";
// logger.info("starting db test");
// await connectDB();
// logger.info("db test finished");
// console.log(config); 

//now we will check the working of loaders/app.js
import { createApp } from "./src/loaders/app.js";
import { config } from "./src/config/index.js";
import logger from "./src/utils/logger.js";
const app = await createApp();
app.listen(config.port,() => {
    logger.info(`server started on port ${config.port}`);
});