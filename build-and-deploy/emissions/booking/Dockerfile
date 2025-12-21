# Multi-stage Dockerfile for Flywise Flight Booking App (v2)
# Optimized for IBM Code Engine deployment

# Stage 1: Build the React application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application source
COPY . .

# Build arguments for environment variables
ARG REACT_APP_ENVIZI_API_KEY
ARG REACT_APP_ENVIZI_API_URL

# Set environment variables for build
ENV REACT_APP_ENVIZI_API_KEY=${REACT_APP_ENVIZI_API_KEY}
ENV REACT_APP_ENVIZI_API_URL=${REACT_APP_ENVIZI_API_URL}

# Build the application
RUN npm run build

# Stage 2: Serve the application with nginx
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy environment variable injection script
COPY env.sh /docker-entrypoint.d/env.sh
RUN chmod +x /docker-entrypoint.d/env.sh

# Expose port 8080 (IBM Code Engine default)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8080/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
