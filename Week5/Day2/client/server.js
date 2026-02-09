const express = require('express');
const path= require('path');
const app=express();
const PORT=5173;
app.use(express.static(path.join(__dirname,"build"))); //express.static se we say ki iss folder k files browser ko dedo.
app.get("/",(req,res)=>{
    res.sendFile(path.join(__dirname,"build","index.html"))
})
app.listen(PORT,()=>{
    console.log(`client running on port ${PORT}`);
});