const winston = require("winston");
const DailyRotateFile= require("winston-daily-rotate-file");
const logDir= "logs";
const env= process.env.NODE_ENV || "development";

const rotateTransport= new DailyRotateFile({
    filename:"logs/app-%DATE%.log",
    datePattern:"YYYY-MM-DD",
    zippedArchive:true,
    maxSize:"10m",
    maxFiles:"7d"
});
const transports=[
    new winston.transports.File({
        filename: `${logDir}/error.log`,
        level:"error",
    }),
    new winston.transports.File({
        filename: `${logDir}/app.log`,
    }),
    rotateTransport,
];
if(env==="development"){
    transports.push(
        new winston.transports.Console({
            format: winston.format.simple(),
        })
    );
}
const logger = winston.createLogger({
  level: env === "production" ? "info" : "debug",
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
//   transports: [
//     new winston.transports.File({
//       filename: "logs/error.log",
//       level: "error",
//     }),
//     new winston.transports.File({
//       filename: "logs/app.log",
//     }),
//   ],
transports,
});

logger.stream={
    write:(message)=>{
        logger.info(message.trim());
    },
};

module.exports=logger;
