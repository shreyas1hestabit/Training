import { ProductRepository } from "../repositories/product.repository.js";

export class ProductService {
  static async getProducts(query) {
    const {  //url k query params hai yeh
      search,
      minPrice,
      maxPrice,
      sort,
      page = 1,
      limit = 10,
      includeDeleted
    } = query;

    const filter = {}; //dynamically conditions add krenge

    // Soft delete filter
    if (!includeDeleted) {
      filter.deletedAt = null; //default behaviour deleted data hide
    }

    // Search
    if (search) {
      filter.name = { $regex: search, $options: "i" }; //partial match kra rhe hai
    }

    // Price range
    if (minPrice || maxPrice) {
      filter.price = {};
      if (minPrice) filter.price.$gte = Number(minPrice);
      if (maxPrice) filter.price.$lte = Number(maxPrice);
    }

    // Sorting
    let sortQuery = { createdAt: -1 };
    if (sort) {
      const [field, order] = sort.split(":");
      sortQuery = { [field]: order === "desc" ? -1 : 1 };
    }

    const skip = (page - 1) * limit;

    return ProductRepository.findWithQuery({
      filter,
      sort: sortQuery,
      skip,
      limit: Number(limit)
    });
  }

  static async softDelete(id) {
    return ProductRepository.update(id, {
      deletedAt: new Date(),
      status: "inactive"
    });
  }
}
