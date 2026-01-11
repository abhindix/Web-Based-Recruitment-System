FROM node:20-alpine

WORKDIR /app

# Install deps first (better layer caching)
COPY package*.json ./
RUN npm ci

# Copy the rest
COPY . .

EXPOSE 5173

# Vite dev server (bind to all interfaces so Docker port mapping works)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]