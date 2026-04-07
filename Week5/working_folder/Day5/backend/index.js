// require("dotenv").config();
// const express= require('express');
// const morgan=require('morgan');
// const fs=require('fs');
// const path=require('path');
// const logger=require('./logger');
// const app=express();
// app.use(
//     morgan("combined",{
//         stream:logger.stream,
//     })
// );
// app.use(express.json());
// let todos=[];
// app.get('/health',(req,res)=>{
//     logger.info("health check hit")
//     res.status(200).json({status:"okay"});
// });
// app.get('/',(req,res)=>{
//     logger.info("started at home")
//     res.send("WELCOME TO TODO APP")
// })
// app.get('/todos',(req,res)=>{
//     logger.info("fetched all todos")
//     res.json(todos);
// });
// app.post('/todos',(req,res)=>{
//     const {title}=req.body;
//     if(!title){
//         logger.warn("todo creation failed: title missing")
//         return res.status(400).json({error:"OOPPSS!!! Title is required"});
//     }
//     const todo={
//         id:Date.now(),
//         title,
//         completed: false,
//     };
//     todos.push(todo);
//     logger.info(`Todo created with id ${todo.id}`);
//     res.status(201).json(todo);
// });
// app.patch("/todos/:id",(req,res)=>{
//     const id = Number(req.params.id);
//     const todo= todos.find(t=>t.id===id);
//     if(!todo){
//         logger.error(`Todo not found with id ${id}`);
//         return res.status(404).json({error: "Todo NOT FOUND!!"});
//     }
//     todo.completed = !todo.completed;
//     logger.info(`Todo updated with id ${id}`);
//     res.json(todo);
// });
// app.use((err,req,res,next)=>{
//     logger.error(err.message);
//     res.status(500).json({error: "internal server error"});
// })
// const PORT = process.env.PORT || 3005;

// app.listen(PORT,()=>{
//     logger.info(`Backend is running on PORT ${PORT}`);
// })

require("dotenv").config();
const express = require('express');
const morgan = require('morgan');
const fs = require('fs');
const path = require('path');
const logger = require('./logger');

const app = express();
app.use(morgan("combined", { stream: logger.stream }));
app.use(express.json());

// --- PERSISTENCE LOGIC ---
const TODO_FILE = path.join(__dirname, "logs", "todos.json");

// Load todos from file on startup
let todos = [];
if (fs.existsSync(TODO_FILE)) {
    try {
        const data = fs.readFileSync(TODO_FILE, 'utf8');
        todos = JSON.parse(data);
        logger.info("Loaded todos from persistent volume");
    } catch (e) {
        logger.error("Failed to parse todos.json, starting fresh");
        todos = [];
    }
}

const saveToVolume = () => {
    fs.writeFileSync(TODO_FILE, JSON.stringify(todos, null, 2));
};
// -------------------------

app.get('/health', (req, res) => {
    res.status(200).json({ status: "okay" });
});

app.get('/api/todos', (req, res) => {
    res.json(todos);
});

app.post('/api/todos', (req, res) => {
    const { title } = req.body;
    if (!title) {
        return res.status(400).json({ error: "Title is required" });
    }
    const todo = { id: Date.now(), title, completed: false };
    todos.push(todo);
    saveToVolume(); // Save to todos.json in logs folder
    res.status(201).json(todo);
});

app.patch("/api/todos/:id", (req, res) => {
    const id = Number(req.params.id);
    const todo = todos.find(t => t.id === id);
    if (!todo) return res.status(404).json({ error: "Not found" });
    
    todo.completed = !todo.completed;
    saveToVolume();
    res.json(todo);
});

const PORT = process.env.PORT || 3005;
app.listen(PORT, () => {
    logger.info(`Backend running on PORT ${PORT}`);
});