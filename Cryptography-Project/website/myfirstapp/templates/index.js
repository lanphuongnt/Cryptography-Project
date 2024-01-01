
// Importing express module
const express = require("express");
 
// Importing mongoose module
const mongoose = require("mongoose");
const port = 80;
const app = express();
 
// Handling the get request
app.get("/", (req, res) => {
    res.send("Hello World");
});
 
// Starting the server on the 80 port
app.listen(port, () => {
    console.log(`The application started
                 successfully on port ${port}`);
});
