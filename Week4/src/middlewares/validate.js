export const validate = (schema) => {
  return (req, res, next) => {
    try {
      const validated = schema.parse({
        body: req.body,
        query: req.query,
        params: req.params
      });

      req.body = validated.body;
      req.validatedQuery = validated.query;
      req.validatedParams = validated.params;

      next();
    } catch (error) {
      next(error);
    }
  };
};
