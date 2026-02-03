// import { Product } from "../models/Product.js";

// export class ProductRepository {
//   static async create(data) {
//     return Product.create(data);
//   }

//   static async findById(id) {
//     return Product.findById(id).populate("createdBy");
//   }

//   static async findPaginated({ page = 1, limit = 10 }) {
//     const skip = (page - 1) * limit;

//     return Product.find()
//       .skip(skip)
//       .limit(limit)
//       .sort({ createdAt: -1 });
//   }

//   static async update(id, data) {
//     return Product.findByIdAndUpdate(id, data, { new: true });
//   }

//   static async softDelete(id) {
//   return Product.findByIdAndUpdate(
//     id,
//     { deletedAt: new Date() },
//     { new: true }
//   );
// }

//   //new method for day3
//   static async findWithQuery({ filter, sort, skip, limit }) {
//   return Product.find(filter)
//     .sort(sort)
//     .skip(skip)
//     .limit(limit);
// }

// }

import Product from "../models/Product.js";

class ProductRepository {
  async create(data) {
    return Product.create(data);
  }

  async findById(id) {
    return Product.findById(id).populate("createdBy");
  }

   // Generic query executor
   // Used by service for search, filters, pagination, sorting
  async findWithQuery({ filter = {}, sort = {}, skip = 0, limit = 10 }) {
    return Product.find(filter)
      .sort(sort)
      .skip(skip)
      .limit(limit);
  }

  async update(id, data) {
    return Product.findByIdAndUpdate(id, data, { new: true });
  }

   // Soft delete (Day 3 requirement)
  async softDelete(id) {
    return Product.findByIdAndUpdate(
      id,
      { deletedAt: new Date() },
      { new: true }
    );
  }
}

export default new ProductRepository();

