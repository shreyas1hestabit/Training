import express from "express"; //express is a http server framework jo routing or middleware system deta hai.
import logger from "../utils/logger.js";
import { connectDB } from "./db.js";
export const createApp = async () => { //yeh function app create krta hai, server abh start nh hota so this becomes reusable
    const app = express(); //yha app exist krti hai
    logger.info("initializing application"); //app initialization ka log
    app.use(express.json()); //jo bh json req aati hai usse parse krta hai.
    logger.info("Middlewares loaded"); 
    await connectDB(); //app tbh ready hogi jb db ready hoga else it will fail.
    app.get("/health",(req,res) => { //basic endpoint which tells that app is alive
        res.json ({status: "OK"});
    });
    logger.info("routes mounted: 1 endpoint");
    return app;
};