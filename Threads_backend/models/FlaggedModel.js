import mongoose from "mongoose";
// Define the schema for flagged users
const flaggedUserSchema = new mongoose.Schema({
  user_id: {
    type: String, // Change to Number if user_id is numeric
    required: true,
  },
  tag: {
    type: String,
    enum: ["Red", "Yellow"], // Assuming 'red' and 'yellow' are the only tags
    required: true,
  },
  classes: {
    type: [String], // Assuming this is an array of strings representing drug classes
    required: true,
  },
  suspicious_word_count: {
    type: Number,
    required: true,
  },
  suspicious_words: {
    type: [String], // Array of suspicious words
    required: true,
  },
});

// Create a model from the schema
const FlaggedUser = mongoose.model("FlaggedUser", flaggedUserSchema);

export default FlaggedUser;
