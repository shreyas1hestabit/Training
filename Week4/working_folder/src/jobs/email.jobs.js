import { Queue } from "bullmq";
import { redisConnection } from "./redis.connection.js";

export const emailQueue = new Queue("emailQueue", {
  connection: redisConnection,
  defaultJobOptions: {
    attempts: 3,           // retry 3 times
    backoff: {
      type: "exponential",
      delay: 2000
    }
  }
});
