const express= require('express');
const mongoose=require('mongoose');
const app=express();
const PORT=3002;
const MONGO_URL=process.env.MONGO_URL;
mongoose
.connect(MONGO_URL)
.then(()=>console.log("mongoDB connected"))
.catch(err=>console.log(err));

app.get('/',(req,res)=>{
    res.send("server running and connected");
});

app.listen(PORT,()=>{
    console.log(`server running on port ${PORT}`);
});