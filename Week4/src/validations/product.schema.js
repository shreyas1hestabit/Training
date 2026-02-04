import { z } from "zod";

export const createProductSchema = z.object({
  body: z.object({
    name: z
      .string()
      .min(2, "Product name must be at least 3 characters")
      .max(100)
      .trim(),

    description: z
      .string()
      .max(500)
      .optional(),

    price: z.coerce
      .number()
      .positive("Price must be greater than 0"),

    category: z
      .string()
      .min(2)
      .max(50),

    stock: z.coerce
      .number()
      .int()
      .min(0),

    status: z
      .enum(["active", "inactive"])
      .default("active")
  })
});
