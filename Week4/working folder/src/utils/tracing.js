import { randomUUID } from "crypto";  //unique ID generate krta hai

export const requestTracer = (req, res, next) => {
  const requestId = req.headers["x-request-id"] || randomUUID();

  req.requestId = requestId;  //poore request lifecycle mein use.
  res.setHeader("X-Request-ID", requestId);

  next();
};
