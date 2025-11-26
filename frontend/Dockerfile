# Base stage
FROM node:20-alpine as base

WORKDIR /app

# Copy package files
COPY package*.json ./


# Development stage
FROM base as development

# Install all dependencies (including dev)
RUN npm install

# Copy source code
COPY . .

EXPOSE 3000

# Development server with hot reload
CMD ["npm", "run", "dev"]


# Build stage
FROM base as builder

# Install dependencies
RUN npm ci --only=production

# Copy source
COPY . .

# Build the application
RUN npm run build


# Production stage - Serve with Nginx
FROM nginx:alpine as production

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
