import { Product } from "../models/Product.js";

export class ProductRepository {
  static async create(data) {
    return Product.create(data);
  }

  static async findById(id) {
    return Product.findById(id).populate("createdBy");
  }

  static async findPaginated({ page = 1, limit = 10 }) {
    const skip = (page - 1) * limit;

    return Product.find()
      .skip(skip)
      .limit(limit)
      .sort({ createdAt: -1 });
  }

  static async update(id, data) {
    return Product.findByIdAndUpdate(id, data, { new: true });
  }

  static async delete(id) {
    return Product.findByIdAndDelete(id);
  }
  //new method for day3
  static async findWithQuery({ filter, sort, skip, limit }) {
  return Product.find(filter)
    .sort(sort)
    .skip(skip)
    .limit(limit);
}

}
