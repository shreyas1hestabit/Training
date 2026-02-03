export const loginUserSchema = z.object({
  body: z.object({
    email: z.string().email(),
    password: z.string().min(1)
  })
});
