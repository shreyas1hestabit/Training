import { z } from "zod";

export const registerUserSchema = z.object({
  body: z.object({
    name: z
      .string()
      .min(3)
      .max(50)
      .trim(),

    email: z
      .string()
      .email("Invalid email format")
      .toLowerCase(),

    password: z
      .string()
      .min(8, "Password must be at least 8 chars")
      .regex(/[A-Z]/, "Must contain uppercase")
      .regex(/[0-9]/, "Must contain number")
      .regex(/[@$!%*?&]/, "Must contain special character")
  })
});
