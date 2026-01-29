//yeh hamre port ko test krne k liye hai. basically hmara code chl bh rha hai ya nh woh chekc krne k liye ek temporary js file.
//import { config } from "./src/config/index.js"; //hm yha woh file with its config import krate hai jiski working hme check krni hai.
//console.log(config);

//to test the working of logger.js
import {config} from "./src/config/index.js";
import logger from "./src/utils/logger.js";
logger.info("Logger is working");
console.log(config);