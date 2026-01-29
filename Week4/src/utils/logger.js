import winston from "winston"; //winston is a logging library which is a professional version of console.log
const logger= winston.createLogger({ //creating a logger instance which will be reused in the whole app 
    level: "info", //we have many levels of logs like info, warn,error, http,verbose etc each with its own severity and fucntion.
    //info has a severity of two
    //winston logs messages at a specified level and all levels that are more severe have a lower numeric value.
    //info describes normal expected behaviour of the application
    format: winston.format.combine( //this decides how logs will be shown 
        winston.format.timestamp(), //will display logs with the timestamp mtlb log kb aaya woh bh show hoga
        winston.format.printf(({level, message, timestamp}) => { //yha hm print format specify kr rhe hai.
            //3 arguments are passed message like log mein kya tha, uska level i.e. info, warn, error etc and lasttly time ki log kb aaya
            return `[${timestamp}] ${level.toUpperCase()}: ${message}`; //return mein order bta diya ki kis order mein output chahiye. now these are dynamic values isliye ${} k andar likha hai. toUpperCase pure level ko uppercase mein bna deta hai.
        })
    ),
    transports: [ //this tells ki log kaha jayega i.e. kaha show hoga and also store hoga.
        new winston.transports.Console(), //terminal mein log ko show krna
        new winston.transports.File({ //log ko log file k andar bh store kra rhe hai for future refrence taaki kbh debugging krni ho toh this would make debugging very easy.
            filename: "src/logs/app.log"
        })
    ]
});
export default logger; //pure project mein import krte skte hai logs ko.