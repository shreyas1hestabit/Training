require("dotenv").config();
const express= require('express');
const morgan=require('morgan');
const fs=require('fs');
const path=require('path');
const logger=require('./logger');
const app=express();
app.use(
    morgan("combined",{
        stream:logger.stream,
    })
);
app.use(express.json());
let todos=[];
app.get('/health',(req,res)=>{
    logger.info("health check hit")
    res.status(200).json({status:"okay"});
});
app.get('/',(req,res)=>{
    logger.info("started at home")
    res.send("WELCOME TO TODO APP")
})
app.get('/todos',(req,res)=>{
    logger.info("fetched all todos")
    res.json(todos);
});
app.post('/todos',(req,res)=>{
    const {title}=req.body;
    if(!title){
        logger.warn("todo creation failed: title missing")
        return res.status(400).json({error:"OOPPSS!!! Title is required"});
    }
    const todo={
        id:Date.now(),
        title,
        completed: false,
    };
    todos.push(todo);
    logger.info(`Todo created with id ${todo.id}`);
    res.status(201).json(todo);
});
app.patch("/todos/:id",(req,res)=>{
    const id = Number(req.params.id);
    const todo= todos.find(t=>t.id===id);
    if(!todo){
        logger.error(`Todo not found with id ${id}`);
        return res.status(404).json({error: "Todo NOT FOUND!!"});
    }
    todo.completed = !todo.completed;
    logger.info(`Todo updated with id ${id}`);
    res.json(todo);
});
app.use((err,req,res,next)=>{
    logger.error(err.message);
    res.status(500).json({error: "internal server error"});
})
const PORT = process.env.PORT || 3005;

app.listen(PORT,()=>{
    logger.info(`Backend is running on PORT ${PORT}`);
})