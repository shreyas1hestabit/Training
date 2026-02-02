import { ProductService } from "../services/product.service.js";

export class ProductController {
  static async getProducts(req, res, next) {
    try {
      const products = await ProductService.getProducts(req.query);

      res.json({
        success: true,
        data: products
      });
    } catch (error) {
      next(error);
    }
  }

  static async deleteProduct(req, res, next) {
    try {
      await ProductService.softDelete(req.params.id);

      res.json({
        success: true,
        message: "Product deleted"
      });
    } catch (error) {
      next(error);
    }
  }
}
