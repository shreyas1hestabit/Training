const express= require("express");
const app= express();
const PORT=3003;
app.get('/',(req,res)=>{
    res.send(`response from backend instance: ${process.env.HOSTNAME}`);
});
app.listen(PORT,()=>{
    console.log(`backend running on port ${PORT}`);
});