import mongoose from "mongoose";
import { z } from "zod"; 
const productSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true
    },
    price: {
      type: Number,
      required: true,
      min: 0
    },
    createdBy: {  //yeh reference hai ki product ka owner user hai
        //basically mongo relation mein kaam aa rha hai.
      type: mongoose.Schema.Types.ObjectId,
      ref: "User"
    },
    status: {
      type: String,
      enum: ["active", "inactive"],
      default: "active"
    }, //day3 
    deletedAt: {
  type: Date,
  default: null
}//till here

  },
  { timestamps: true }
);

productSchema.index({ status: 1, createdAt: -1 });

export const Product = mongoose.model("Product", productSchema);

export const updateProductSchema = z.object({
  body: z.object({
    name: z.string().min(3).optional(),
    description: z.string().max(500).optional(),
    price: z.number().positive().optional(),
    category: z.string().optional(),
    stock: z.number().int().min(0).optional(),
    status: z.enum(["active", "inactive"]).optional()
  }),
  params: z.object({
    id: z.string().length(24, "Invalid Mongo ObjectId")
  })
});

