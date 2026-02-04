import logger from "../utils/logger.js";

export const requestLogger = (req, res, next) => {
  logger.info(`Incoming ${req.method} ${req.originalUrl}`, {
    requestId: req.requestId
  });

  res.on("finish", () => {
    logger.info(
      `Response ${res.statusCode} ${req.method} ${req.originalUrl}`,
      { requestId: req.requestId }
    );
  });

  next();
};
