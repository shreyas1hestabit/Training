// export const errorHandler = (err, req, res, next) => {
//   res.status(err.statusCode || 500).json({
//     success: false,
//     message: err.message || "Internal Server Error",
//     code: err.code || "SERVER_ERROR",
//     timestamp: new Date().toISOString(),
//     path: req.originalUrl
//   });
// };
export const errorHandler = (err, req, res, next) => {
  if (err.name === "ZodError") {
    return res.status(400).json({
      success: false,
      message: "Validation failed",
      code: "VALIDATION_ERROR"
    });
  }

  if (err.name === "CastError") {
    return res.status(400).json({
      success: false,
      message: "Invalid data type",
      code: "INVALID_INPUT"
    });
  }

  return res.status(500).json({
    success: false,
    message: "Internal Server Error"
  });
};

