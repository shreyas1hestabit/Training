// import { ProductService } from "../services/product.service.js";

// export class ProductController {
//   static async getProducts(req, res, next) {
//     try {
//       const products = await ProductService.getProducts(req.query);

//       res.json({
//         success: true,
//         data: products
//       });
//     } catch (error) {
//       next(error);
//     }
//   }

//   static async deleteProduct(req, res, next) {
//     try {
//       await ProductService.softDelete(req.params.id);

//       res.json({
//         success: true,
//         message: "Product deleted"
//       });
//     } catch (error) {
//       next(error);
//     }
//   }
// }


import { ProductService } from "../services/product.service.js";

export class ProductController {

  
   // GET /products

  static async getProducts(req, res, next) {
    try {
      const products = await ProductService.getProducts(req.query);

      res.status(200).json({
        success: true,
        data: products
      });
    } catch (error) {
      next(error);
    }
  }

  
   //DELETE /products/:id
   //Soft delete
  static async deleteProduct(req, res, next) {
    try {
      const deletedProduct = await ProductService.softDelete(req.params.id);

      res.status(200).json({
        success: true,
        message: "Product deleted successfully",
        data: deletedProduct
      });
    } catch (error) {
      next(error);
    }
  }
}
