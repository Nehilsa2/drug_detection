import mongoose from "mongoose";
import Conversation from "./conversationModel";

const ConversationSchema = new mongoose.Schema({
  conversation_id: {
    type: String,
    required: true,
  },
  members: {
    type: [String],
    required: true,
    validate: {
      validator: (array) => array.length === 2,
      message: "Members array must contain exactly two members.",
    },
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

export default Conversation = mongoose.model(
  "Conversation",
  ConversationSchema
);
