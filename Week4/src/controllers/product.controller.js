// // import { ProductService } from "../services/product.service.js";

// // export class ProductController {
// //   static async getProducts(req, res, next) {
// //     try {
// //       const products = await ProductService.getProducts(req.query);

// //       res.json({
// //         success: true,
// //         data: products
// //       });
// //     } catch (error) {
// //       next(error);
// //     }
// //   }

// //   static async deleteProduct(req, res, next) {
// //     try {
// //       await ProductService.softDelete(req.params.id);

// //       res.json({
// //         success: true,
// //         message: "Product deleted"
// //       });
// //     } catch (error) {
// //       next(error);
// //     }
// //   }
// // }


// import { ProductService } from "../services/product.service.js";

// export class ProductController {

  
//    // GET /products

//   static async getProducts(req, res, next) {
//     try {
//       const products = await ProductService.getProducts(req.query);

//       res.status(200).json({
//         success: true,
//         data: products
//       });
//     } catch (error) {
//       next(error);
//     }
//   }

  
//    //DELETE /products/:id
//    //Soft delete
//   static async deleteProduct(req, res, next) {
//     try {
//       const deletedProduct = await ProductService.softDelete(req.params.id);

//       res.status(200).json({
//         success: true,
//         message: "Product deleted successfully",
//         data: deletedProduct
//       });
//     } catch (error) {
//       next(error);
//     }
//   }
// }


import ProductRepository from "../repositories/product.repository.js";

const ProductController = {
  createProduct: async (req, res) => {
    try {
      const product = await ProductRepository.create(req.body);
      res.status(201).json(product);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  },

  getProducts: async (req, res) => {
    try {
      const products = await ProductRepository.findWithQuery({});
      res.json(products);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  },

  deleteProduct: async (req, res) => {
    try {
      const deleted = await ProductRepository.softDelete(req.params.id);
      res.json(deleted);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  }
};

export default ProductController;
