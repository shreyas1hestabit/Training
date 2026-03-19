const express = require('express');
const mongoose = require('mongoose');
const app = express();
const PORT = 3002;

// Use the environment variable provided by docker-compose
const MONGO_URL = process.env.MONGO_URL || "mongodb://mongo:27017/appdb";

const connectWithRetry = () => {
    console.log('MongoDB connection with retry');
    mongoose.connect(MONGO_URL)
        .then(() => console.log(" MongoDB connected"))
        .catch(err => {
            console.log(" MongoDB connection failed, retrying in 5 seconds...", err);
            setTimeout(connectWithRetry, 5000); // Retry logic
        });
};

connectWithRetry();

app.get('/', (req, res) => {
    res.send("Backend Server is running and connected to Mongo!");
});

app.listen(PORT, () => {
    console.log(` Server running on port ${PORT}`);
});