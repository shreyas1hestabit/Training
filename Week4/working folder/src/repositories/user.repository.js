import { User } from "../models/User.js";

export class UserRepository {
  static async create(data) {
    return User.create(data);
  }

  static async findById(id) {
    return User.findById(id);
  }

  static async findPaginated({ page = 1, limit = 10 }) {
    const skip = (page - 1) * limit;

    return User.find()
      .skip(skip)
      .limit(limit)
      .sort({ createdAt: -1 });
  }

  static async update(id, data) {
    return User.findByIdAndUpdate(id, data, { new: true });
  }

  static async delete(id) {
    return User.findByIdAndDelete(id);
  }
}
