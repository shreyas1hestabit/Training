import mongoose from "mongoose"; //mongoose lib ko import kr rhe hai coz it provides a structured, schema based solution
//iska main kaam is db se baat krna
import logger from "../utils/logger.js"; //ab hm console.log nh central logger which we created use krenge
import {config} from "../config/index.js"; 
export const connectDB = async () => {  //yeh db ka connection hai and db ka connection is always asynchronus
    try{
        await mongoose.connect(config.dbUrl); //jbtk db ready na ho app aage nh bdega
        logger.info("Database Connected"); //after connection log info with message database connected.
    } catch (error){
        logger.error("Database connection failed"); //agr error aaye toh log error with the failed message.
        process.exit(1); //db k bina app chlna hi nh chahiye
    }
};