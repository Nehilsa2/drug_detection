import path from "path";
import express from "express";
import dotenv from "dotenv";
import connectDB from "./db/connectDB.js";
import cookieParser from "cookie-parser";
import userRoutes from "./routes/userRoutes.js";
import postRoutes from "./routes/postRoutes.js";
import messageRoutes from "./routes/messageRoutes.js";
import { v2 as cloudinary } from "cloudinary";
import { app, server } from "./socket/socket.js";
import job from "./cron/cron.js";
import cors from 'cors';

const allowedorigins = ["https://threads-frontend-8fph.onrender.com",
  "https://jhanducoder-drug-detection-ml.hf.space/admin"];

app.use(cors({
   origin: allowedorigins, 
  credentials: true,
}));

dotenv.config();

connectDB();
job.start();

const PORT = process.env.PORT || 5000;
const __dirname = path.resolve();

cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET,
});

// Middlewares

app.use(express.json({ limit: "50mb" })); // To parse JSON data in the req.body
app.use(express.urlencoded({ extended: true })); // To parse form data in the req.body
app.use(cookieParser());

// Routes
app.use("/api/users", userRoutes);
app.use("/api/posts", postRoutes);
app.use("/api/messages", messageRoutes);

// http://localhost:5000 => backend,frontend

// if (process.env.NODE_ENV === "production") {
//   app.use(express.static(path.join(__dirname, "/Threads_frontend/dist")));

//   // react app
//   app.get("*", (req, res) => {
//     res.sendFile(path.resolve(__dirname, "Threads_frontend", "dist", "index.html"));
//   });
// }
app.get("/",(req,res) => {
  res.send("🚀 Thread Backend is live and running")
});
  

server.listen(PORT, () =>
  console.log(`Server started at http://localhost:${PORT}`)
);
