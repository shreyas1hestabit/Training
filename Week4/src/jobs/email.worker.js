import { Worker } from "bullmq";
import { redisConnection } from "./redis.connection.js";
import logger from "../utils/logger.js";

const worker = new Worker(
  "emailQueue",
  async (job) => {
    logger.info(
      `Processing email job for ${job.data.email}`,
      { requestId: job.data.requestId }
    );

    // Fake email delay
    await new Promise((res) => setTimeout(res, 2000));

    if (!job.data.email) {
      throw new Error("Email missing");
    }

    logger.info(
      `Email sent successfully to ${job.data.email}`,
      { requestId: job.data.requestId }
    );
  },
  {
    connection: redisConnection
  }
);

worker.on("failed", (job, err) => {
  logger.error(
    `Email job failed: ${err.message}`,
    { requestId: job.data?.requestId }
  );
});
