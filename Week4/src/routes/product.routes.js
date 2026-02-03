// import { Router } from "express";
// import { ProductController } from "../controllers/product.controller.js";


// const router = Router();

// router.get("/products", ProductController.getProducts);
// router.delete("/products/:id", ProductController.deleteProduct);

// export default router;

import { ProductController } from "../controllers/product.controller";

const router = express.Router();
router.get("/",ProductController.getProducts);
router.delete("/:id",ProductController.deleteProduct);
export default router;