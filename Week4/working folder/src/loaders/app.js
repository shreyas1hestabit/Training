// import express from "express"; //express is a http server framework jo routing or middleware system deta hai.
// import logger from "../utils/logger.js";
// import { connectDB } from "./db.js";
// import { errorHandler } from "../middlewares/error.middleware.js";
// export const createApp = async () => { //yeh function app create krta hai, server abh start nh hota so this becomes reusable
//     const app = express(); //yha app exist krti hai
//     logger.info("initializing application"); //app initialization ka log
//     app.use(express.json()); //jo bh json req aati hai usse parse krta hai.
//     logger.info("Middlewares loaded"); 
//     await connectDB(); //app tbh ready hogi jb db ready hoga else it will fail.
//     app.get("/health",(req,res) => { //basic endpoint which tells that app is alive
//         res.json ({status: "OK"});
//     });
//     logger.info("routes mounted: 1 endpoint");

//     //day3
// app.use(errorHandler);

//     return app;
// };

import productRoutes from "../routes/product.routes.js";
import express from "express";
import helmet from "helmet";
import cors from "cors";
import rateLimit from "express-rate-limit";
import logger from "../utils/logger.js";
import { requestTracer } from "../utils/tracing.js";
import { connectDB } from "./db.js";
import { securityMiddleware } from "../middlewares/security.js";
import { errorHandler } from "../middlewares/error.middleware.js";
import { requestLogger } from "../middlewares/requestLogger.js";

export const createApp = async () => {
  const app = express();

   logger.info("Initializing application");
/*
//   securityMiddleware(app); 

//   await connectDB();

//   app.use((req, res, next) => {
//     console.log(" Request Debug:", {
//       method: req.method,
//       path: req.path,
//       contentType: req.get("Content-Type"),
//       body: req.body,
//       bodyIsUndefined: req.body === undefined
//     });
//     next();
//   });

//   app.get("/health", (req, res) => {
//     res.json({ status: "OK" });
//   });

//   app.use("/products",productRoutes);
//   app.use(errorHandler);

//   return app;
// };
*/
app.use(helmet());
  
  app.use(
    cors({
      origin: ["http://localhost:3000"],
      methods: ["GET", "POST", "PUT", "DELETE"],
      allowedHeaders: ["Content-Type", "Authorization"],
      credentials: true
    })
  );

  app.use(
    rateLimit({
      windowMs: 15 * 60 * 1000,
      max: 100,
      standardHeaders: true,
      legacyHeaders: false,
      message: "Too many requests, please try again later"
    })
  );

  // Body parser - THIS MUST COME BEFORE ROUTES
  app.use(express.json({ limit: "10kb" }));
  app.use(express.urlencoded({ extended: true }));

  app.use(requestTracer);
  app.use(requestLogger);

  await connectDB();

  app.get("/health", (req, res) => {
    res.json({ status: "OK" });
  });

  app.use("/products", productRoutes);
  
  // Error handler MUST be last
  app.use(errorHandler);

  return app;
};
