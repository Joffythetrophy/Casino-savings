FROM node:18-alpine

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./
COPY frontend/yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy frontend code
COPY frontend/ .

# Build the app
RUN yarn build

# Install serve to run the built app
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start frontend
CMD ["serve", "-s", "build", "-l", "3000"]
