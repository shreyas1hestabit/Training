import mongoose from "mongoose";
const userSchema = new mongoose.Schema( //schema mtlb db ka blueprint bnaya
    {
        firstName:{
            type: String,
            required: true,
            trim: true //data ko clean format mein krne k liye use hota hai. like whitespaces remove kr dega.
        },
        lastName:{
            type:String,
            required:true,
            trim:true
        },
        email:{
            type:String,
            required: true,
            unique: true,
            lowercase: true
        },
        password:{
            type: String,
            required: true,
            minlength:6
        },
        status:{
            type:String,
            enum:["active","inactive"], //sirf yhi values allowed hai
            default:"active"
        }
    },
    {
        timestamps: true //mongo automatically add krega createdAt and updatedAt
    }
);

//pre save hook -> save hone se pehle wala hook
userSchema.pre("save",function(next){
    if(!this.isModified("password")) return next(); //agr pass change nh hua toh rehash mt kro aage move kro
    this.password="hashed_" + this.password; //abh dummy hash kr rhe hai qk pass kbh raw store nh hota
});
userSchema.virtual("fullName").get(function(){  //virtual mtlb db mein store na but response mein dikhe
    return `${this.firstName} ${this.lastName}`; //full name show hoga instead of first name and last name
    // isse db size nh bdega
});
userSchema.index({status:1,createdAt:-1}); //index query ko fast bnata hai.
// 2 usecases possible-> active and latest.
// 1: ascending and -1:descending
export const User =  mongoose.model("User",userSchema)