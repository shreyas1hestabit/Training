const express= require('express');
const app=express();
app.get('/',(req,res)=>{
    res.send("running backend over https");
});
app.listen(3000,()=>{
    console.log("backend running on port 3000");
});