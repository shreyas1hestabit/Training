import { Router } from "express";
import { ProductController } from "../controllers/product.controller.js";

const router = Router();

router.get("/products", ProductController.getProducts);
router.delete("/products/:id", ProductController.deleteProduct);

export default router;
