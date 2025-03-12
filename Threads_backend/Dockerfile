# Use official Node.js image
FROM node:18

# Set the working directory inside the container
WORKDIR /app/backend

# Copy package.json and package-lock.json first (for better caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all backend files into the container
COPY . .

# Expose the backend port
EXPOSE 5000

# Start the backend using "npm run dev"
CMD ["npm", "run", "dev"]
