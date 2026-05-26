# Backend Development Guide

## Overview

This comprehensive guide covers all aspects of backend development for the Turbonomic Resource Dashboard, including Node.js/Express server architecture, API design, Turbonomic integration, middleware patterns, security, and performance optimization.

**Technology Stack:**
- Node.js (Runtime Environment)
- Express 4.18.2 (Web Framework)
- Axios 1.6.0 (HTTP Client)
- CORS 2.8.5 (Cross-Origin Resource Sharing)
- dotenv 16.4.0 (Environment Configuration)

---

## Table of Contents

### Part 1: Server Architecture & Setup
1. [Application Structure](#1-application-structure)
2. [Express Server Setup](#2-express-server-setup)
3. [Middleware Configuration](#3-middleware-configuration)
4. [Health Check Endpoints](#4-health-check-endpoints)

### Part 2: API Design & Routing
5. [RESTful API Design](#5-restful-api-design)
6. [Route Organization](#6-route-organization)
7. [Request Validation](#7-request-validation)
8. [Response Formatting](#8-response-formatting)

### Part 3: Turbonomic Integration
9. [Proxy Architecture](#9-proxy-architecture)
10. [Turbonomic API Client](#10-turbonomic-api-client)
11. [Authentication & Authorization](#11-authentication--authorization)
12. [API Endpoints](#12-api-endpoints)

### Part 4: Error Handling & Security
13. [Error Handling Patterns](#13-error-handling-patterns)
14. [Security Best Practices](#14-security-best-practices)
15. [Input Sanitization](#15-input-sanitization)
16. [Rate Limiting](#16-rate-limiting)

### Part 5: Performance & Monitoring
17. [Performance Optimization](#17-performance-optimization)
18. [Caching Strategies](#18-caching-strategies)
19. [Logging & Monitoring](#19-logging--monitoring)
20. [Testing Strategies](#20-testing-strategies)

---

# Part 1: Server Architecture & Setup

## 1. Application Structure

```
backend/
├── src/
│   ├── server.js              # Main application entry point
│   ├── turbonomic-proxy.js    # Turbonomic API proxy router
│   ├── middleware/            # Custom middleware
│   │   ├── auth.js
│   │   ├── errorHandler.js
│   │   └── validation.js
│   ├── routes/                # Route handlers
│   │   ├── operations.js
│   │   └── turbonomic.js
│   ├── services/              # Business logic
│   │   ├── operationsService.js
│   │   └── turbonomicService.js
│   ├── utils/                 # Utility functions
│   │   ├── logger.js
│   │   └── exec.js
│   └── config/                # Configuration files
│       └── index.js
├── Dockerfile                 # Container definition
├── package.json              # Dependencies
└── .env                      # Environment variables
```

### Architectural Principles

**1. Separation of Concerns**

```javascript
// ✅ Good: Separate routing, business logic, and data access

// routes/operations.js
router.post('/namespaces', operationsController.getNamespaces);

// controllers/operations.js
async function getNamespaces(req, res, next) {
  try {
    const namespaces = await operationsService.fetchNamespaces(req.body);
    res.json({ namespaces, timestamp: new Date().toISOString() });
  } catch (error) {
    next(error);
  }
}

// services/operations.js
async function fetchNamespaces({ clusterToken, clusterServer }) {
  // Business logic implementation
  const command = `oc get projects --server="${clusterServer}" --token="${clusterToken}"`;
  const output = await execAsync(command);
  return parseNamespaces(output);
}
```

**2. Modular Design**

```javascript
// ✅ Good: Modular router structure
const express = require('express');
const turbonomicRouter = require('./turbonomic-proxy');
const operationsRouter = require('./routes/operations');

app.use('/api/turbonomic', turbonomicRouter);
app.use('/api/operations', operationsRouter);
```

**3. Dependency Injection**

```javascript
// ✅ Good: Inject dependencies
class TurbonomicService {
  constructor(httpClient, config) {
    this.httpClient = httpClient;
    this.config = config;
  }
  
  async getActions() {
    return this.httpClient.get(`${this.config.url}/api/v3/actions`);
  }
}

// Usage
const service = new TurbonomicService(axios, config);
```

## 2. Express Server Setup

### Basic Configuration

```javascript
const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 4000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Routes
app.use('/api/turbonomic', require('./turbonomic-proxy'));
app.use('/api/operations', require('./routes/operations'));

// Error handling
app.use(errorHandler);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found', path: req.path });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;
```

### Production Configuration

```javascript
const express = require('express');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');

const app = express();

// Security middleware
app.use(helmet());

// Compression
app.use(compression());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);

// Body parsing with size limits
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
```

## 3. Middleware Configuration

### CORS Configuration

```javascript
// Development CORS
app.use(cors());

// Production CORS with specific origins
const corsOptions = {
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true,
  optionsSuccessStatus: 200,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};
app.use(cors(corsOptions));
```

### Request Logging

```javascript
// Simple logging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Enhanced logging with request ID
const { v4: uuidv4 } = require('uuid');

app.use((req, res, next) => {
  req.id = uuidv4();
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log({
      requestId: req.id,
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration: `${duration}ms`,
      timestamp: new Date().toISOString()
    });
  });
  
  next();
});
```

### Authentication Middleware

```javascript
// Token validation
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Authentication required' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ message: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
}

// Apply to protected routes
app.use('/api/protected', authenticateToken);
```

## 4. Health Check Endpoints

### Kubernetes Probes

```javascript
// Liveness probe - is the application running?
app.get('/health/live', (req, res) => {
  res.status(200).json({ status: 'alive' });
});

// Readiness probe - is the application ready to serve traffic?
app.get('/health/ready', async (req, res) => {
  try {
    // Check dependencies
    await checkDatabase();
    await checkExternalAPIs();
    
    res.status(200).json({ status: 'ready' });
  } catch (error) {
    res.status(503).json({ 
      status: 'not ready',
      error: error.message 
    });
  }
});

// General health check
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy', 
    service: 'operations-dashboard-backend',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});
```

---

# Part 2: API Design & Routing

## 5. RESTful API Design

### HTTP Methods

```javascript
// GET - Retrieve resources
app.get('/api/resources', async (req, res) => {
  const resources = await resourceService.findAll();
  res.json(resources);
});

// POST - Create new resource
app.post('/api/resources', async (req, res) => {
  const resource = await resourceService.create(req.body);
  res.status(201).json(resource);
});

// PUT - Update entire resource
app.put('/api/resources/:id', async (req, res) => {
  const resource = await resourceService.update(req.params.id, req.body);
  res.json(resource);
});

// PATCH - Partial update
app.patch('/api/resources/:id', async (req, res) => {
  const resource = await resourceService.patch(req.params.id, req.body);
  res.json(resource);
});

// DELETE - Remove resource
app.delete('/api/resources/:id', async (req, res) => {
  await resourceService.delete(req.params.id);
  res.status(204).send();
});
```

### URL Structure

```javascript
// ✅ Good: Clear, hierarchical URLs
GET    /api/turbonomic/entities
GET    /api/turbonomic/entities/:id
POST   /api/turbonomic/actions
GET    /api/operations/namespaces
POST   /api/operations/pod-metrics

// ❌ Avoid: Unclear or inconsistent URLs
GET    /api/getEntities
POST   /api/create-action
GET    /api/namespace_list
```

## 6. Route Organization

### Router Pattern

```javascript
// routes/operations.js
const express = require('express');
const router = express.Router();
const operationsController = require('../controllers/operations');

// List namespaces
router.post('/namespaces', operationsController.getNamespaces);

// Get pod metrics
router.post('/pod-metrics', operationsController.getPodMetrics);

// Start simulation
router.post('/start-simulation', operationsController.startSimulation);

module.exports = router;
```

### Controller Pattern

```javascript
// controllers/operations.js
const operationsService = require('../services/operationsService');

exports.getNamespaces = async (req, res, next) => {
  try {
    const { clusterToken, clusterServer } = req.body;
    
    if (!clusterToken || !clusterServer) {
      return res.status(400).json({
        message: 'Cluster credentials are required',
        requiresCredentials: true
      });
    }
    
    const namespaces = await operationsService.fetchNamespaces({
      clusterToken,
      clusterServer
    });
    
    res.json({
      namespaces,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    next(error);
  }
};
```

## 7. Request Validation

### Express Validator

```javascript
const { body, validationResult } = require('express-validator');

// Validation middleware
const validateNamespaceRequest = [
  body('clusterToken')
    .notEmpty()
    .withMessage('Cluster token is required'),
  body('clusterServer')
    .isURL()
    .withMessage('Valid cluster server URL is required'),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    next();
  }
];

// Apply validation
router.post('/namespaces', validateNamespaceRequest, handler);
```

### Manual Validation

```javascript
function validateCredentials(req, res, next) {
  const { turboHost, turboUsername, turboPassword } = req.body;
  
  if (!turboHost || !turboUsername || !turboPassword) {
    return res.status(400).json({
      error: 'Missing required credentials',
      required: ['turboHost', 'turboUsername', 'turboPassword']
    });
  }
  
  // Validate URL format
  try {
    new URL(turboHost);
  } catch (error) {
    return res.status(400).json({
      error: 'Invalid turboHost URL format'
    });
  }
  
  next();
}
```

## 8. Response Formatting

### Consistent Response Structure

```javascript
// Success response
{
  "data": { /* response data */ },
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "success"
}

// Error response
{
  "error": "Error message",
  "message": "Detailed error description",
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "error"
}

// Paginated response
{
  "data": [ /* items */ ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 100,
    "totalPages": 5
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Response Helper

```javascript
class ResponseFormatter {
  static success(res, data, statusCode = 200) {
    res.status(statusCode).json({
      data,
      timestamp: new Date().toISOString(),
      status: 'success'
    });
  }
  
  static error(res, message, statusCode = 500, details = null) {
    res.status(statusCode).json({
      error: message,
      details,
      timestamp: new Date().toISOString(),
      status: 'error'
    });
  }
  
  static paginated(res, data, pagination) {
    res.json({
      data,
      pagination,
      timestamp: new Date().toISOString()
    });
  }
}

// Usage
ResponseFormatter.success(res, { users: [] });
ResponseFormatter.error(res, 'Not found', 404);
```

---

# Part 3: Turbonomic Integration

## 9. Proxy Architecture

### Why Use a Proxy?

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │ ──────> │   Backend   │ ──────> │ Turbonomic  │
│   (React)   │ <────── │   (Proxy)   │ <────── │     API     │
└─────────────┘         └─────────────┘         └─────────────┘
     :3000                   :4000                  :443/80
```

**Benefits:**
1. **Security** - Credentials never exposed to frontend
2. **CORS** - Bypass cross-origin restrictions
3. **Rate Limiting** - Control API request frequency
4. **Caching** - Reduce redundant API calls
5. **Error Handling** - Centralized error management
6. **Logging** - Track API usage and issues

## 10. Turbonomic API Client

### Basic Proxy Implementation

```javascript
// turbonomic-proxy.js
const express = require('express');
const axios = require('axios');
const https = require('https');

const router = express.Router();

// Proxy all Turbonomic API requests
router.all('/*', async (req, res) => {
  try {
    const { turboHost, turboUsername, turboPassword } = req.body;
    
    // Validate credentials
    if (!turboHost || !turboUsername || !turboPassword) {
      return res.status(400).json({
        error: 'Missing required Turbonomic credentials'
      });
    }
    
    // Build target URL
    const targetUrl = `${turboHost}${req.path}`;
    
    // Make request to Turbonomic
    const response = await axios({
      method: req.method,
      url: targetUrl,
      data: req.body,
      params: req.query,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      auth: {
        username: turboUsername,
        password: turboPassword
      },
      httpsAgent: new https.Agent({
        rejectUnauthorized: false // For self-signed certificates
      })
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('Turbonomic API Error:', error.message);
    
    const statusCode = error.response?.status || 500;
    const errorMessage = error.response?.data?.message || error.message;
    
    res.status(statusCode).json({
      error: 'Failed to fetch data from Turbonomic',
      message: errorMessage
    });
  }
});

module.exports = router;
```

### Service Layer Implementation

```javascript
// services/turbonomicService.js
const axios = require('axios');
const https = require('https');

class TurbonomicService {
  constructor() {
    this.httpsAgent = new https.Agent({
      rejectUnauthorized: false
    });
  }
  
  async makeRequest(config, credentials) {
    const { turboHost, turboUsername, turboPassword } = credentials;
    
    return axios({
      ...config,
      baseURL: turboHost,
      auth: {
        username: turboUsername,
        password: turboPassword
      },
      httpsAgent: this.httpsAgent,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...config.headers
      }
    });
  }
  
  async getEntities(credentials) {
    const response = await this.makeRequest({
      method: 'GET',
      url: '/api/v3/entities'
    }, credentials);
    
    return response.data;
  }
  
  async getPendingActions(credentials) {
    const response = await this.makeRequest({
      method: 'GET',
      url: '/api/v3/actions',
      params: {
        state: 'PENDING_ACCEPT'
      }
    }, credentials);
    
    return response.data;
  }
  
  async executeAction(actionId, credentials) {
    const response = await this.makeRequest({
      method: 'POST',
      url: `/api/v3/actions/${actionId}/execute`
    }, credentials);
    
    return response.data;
  }
}

module.exports = new TurbonomicService();
```

## 11. Authentication & Authorization

### Basic Authentication

```javascript
// Turbonomic uses HTTP Basic Auth
const auth = {
  username: process.env.TURBONOMIC_USERNAME,
  password: process.env.TURBONOMIC_PASSWORD
};

axios.get(url, { auth });
```

### Token-Based Authentication

```javascript
// If using token-based auth
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};

axios.get(url, { headers });
```

## 12. API Endpoints

### Get Entities

```javascript
router.post('/api/turbonomic/entities', async (req, res) => {
  try {
    const { turboHost, turboUsername, turboPassword } = req.body;
    
    const entities = await turbonomicService.getEntities({
      turboHost,
      turboUsername,
      turboPassword
    });
    
    res.json(entities);
  } catch (error) {
    res.status(500).json({
      error: 'Failed to fetch entities',
      message: error.message
    });
  }
});
```

### Get Pending Actions

```javascript
router.post('/api/turbonomic/actions', async (req, res) => {
  try {
    const { turboHost, turboUsername, turboPassword } = req.body;
    
    const actions = await turbonomicService.getPendingActions({
      turboHost,
      turboUsername,
      turboPassword
    });
    
    res.json(actions);
  } catch (error) {
    res.status(500).json({
      error: 'Failed to fetch actions',
      message: error.message
    });
  }
});
```

---

# Part 4: Error Handling & Security

## 13. Error Handling Patterns

### Centralized Error Handler

```javascript
// middleware/errorHandler.js
function errorHandler(err, req, res, next) {
  console.error('Error:', {
    message: err.message,
    stack: err.stack,
    requestId: req.id,
    path: req.path,
    method: req.method
  });

  const statusCode = err.statusCode || err.status || 500;
  
  res.status(statusCode).json({
    error: err.message || 'Internal server error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
}

module.exports = errorHandler;
```

### Custom Error Classes

```javascript
// errors/AppError.js
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

class ValidationError extends AppError {
  constructor(message) {
    super(message, 400);
  }
}

class AuthenticationError extends AppError {
  constructor(message = 'Authentication required') {
    super(message, 401);
  }
}

class NotFoundError extends AppError {
  constructor(message = 'Resource not found') {
    super(message, 404);
  }
}

module.exports = { 
  AppError, 
  ValidationError, 
  AuthenticationError, 
  NotFoundError 
};
```

### Async Error Handling

```javascript
// Wrapper for async route handlers
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Usage
router.get('/data', asyncHandler(async (req, res) => {
  const data = await fetchData();
  res.json(data);
}));
```

## 14. Security Best Practices

### Environment Variables

```javascript
// ✅ Good: Use environment variables
require('dotenv').config();

const config = {
  turbonomic: {
    url: process.env.TURBONOMIC_URL,
    username: process.env.TURBONOMIC_USERNAME,
    password: process.env.TURBONOMIC_PASSWORD
  },
  server: {
    port: process.env.PORT || 4000,
    nodeEnv: process.env.NODE_ENV || 'development'
  }
};

// ❌ Bad: Hardcoded credentials
const username = 'admin';
const password = 'password123';
```

### Helmet for Security Headers

```javascript
const helmet = require('helmet');

app.use(helmet());

// Custom configuration
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"]
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));
```

### Secure Command Execution

```javascript
// ✅ Good: Validate and sanitize
function executeSecureCommand(command, args) {
  const allowedCommands = ['oc', 'kubectl'];
  
  if (!allowedCommands.includes(command)) {
    throw new Error('Command not allowed');
  }
  
  const sanitizedArgs = args.map(arg => {
    return arg.replace(/[;&|`$()]/g, '');
  });
  
  return execAsync(`${command} ${sanitizedArgs.join(' ')}`);
}

// ❌ Bad: Direct execution
const userInput = req.body.command;
exec(userInput); // Vulnerable to command injection
```

## 15. Input Sanitization

### Sanitize HTML

```javascript
const sanitizeHtml = require('sanitize-html');

function sanitizeInput(input) {
  if (typeof input === 'string') {
    return sanitizeHtml(input, {
      allowedTags: [],
      allowedAttributes: {}
    });
  }
  return input;
}

// Apply to request body
app.use((req, res, next) => {
  if (req.body) {
    Object.keys(req.body).forEach(key => {
      req.body[key] = sanitizeInput(req.body[key]);
    });
  }
  next();
});
```

## 16. Rate Limiting

### Express Rate Limit

```javascript
const rateLimit = require('express-rate-limit');

// General rate limiter
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  message: 'Too many requests, please try again later'
});

app.use('/api/', limiter);

// Stricter limit for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: 'Too many authentication attempts'
});

app.use('/api/auth/', authLimiter);
```

---

# Part 5: Performance & Monitoring

## 17. Performance Optimization

### Response Compression

```javascript
const compression = require('compression');

app.use(compression({
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  },
  level: 6
}));
```

### Connection Pooling

```javascript
const https = require('https');

const httpsAgent = new https.Agent({
  keepAlive: true,
  keepAliveMsecs: 30000,
  maxSockets: 50,
  maxFreeSockets: 10,
  timeout: 60000
});

const apiClient = axios.create({
  httpsAgent
});
```

## 18. Caching Strategies

### In-Memory Cache

```javascript
const NodeCache = require('node-cache');

const cache = new NodeCache({
  stdTTL: 300, // 5 minutes
  checkperiod: 60
});

function cacheMiddleware(duration) {
  return (req, res, next) => {
    const key = `${req.method}:${req.originalUrl}`;
    const cachedResponse = cache.get(key);
    
    if (cachedResponse) {
      return res.json(cachedResponse);
    }
    
    const originalJson = res.json.bind(res);
    res.json = (body) => {
      cache.set(key, body, duration);
      return originalJson(body);
    };
    
    next();
  };
}

// Usage
app.get('/api/data', cacheMiddleware(300), handler);
```

## 19. Logging & Monitoring

### Winston Logger

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({ 
      filename: 'logs/error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: 'logs/combined.log' 
    })
  ]
});

// Usage
logger.info('Server started', { port: PORT });
logger.error('Database error', { error: err.message });
```

## 20. Testing Strategies

### Unit Tests with Jest

```javascript
const request = require('supertest');
const app = require('../src/server');

describe('Health Check Endpoints', () => {
  test('GET /health returns 200', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('status', 'healthy');
  });
});

describe('Operations API', () => {
  test('POST /api/operations/namespaces requires credentials', async () => {
    const response = await request(app)
      .post('/api/operations/namespaces')
      .send({});
    
    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('requiresCredentials', true);
  });
});
```

### Integration Tests

```javascript
const nock = require('nock');

describe('Turbonomic Proxy', () => {
  beforeEach(() => {
    nock('https://turbonomic.example.com')
      .get('/api/v3/markets')
      .reply(200, { markets: [] });
  });

  afterEach(() => {
    nock.cleanAll();
  });

  test('Proxy forwards request', async () => {
    const response = await request(app)
      .get('/api/turbonomic/api/v3/markets');
    
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('markets');
  });
});
```

---

## Best Practices Summary

### DO ✅

- Use environment variables for configuration
- Implement proper error handling
- Use async/await for asynchronous operations
- Implement request logging
- Validate and sanitize user input
- Use middleware for cross-cutting concerns
- Implement health check endpoints
- Use connection pooling
- Implement rate limiting
- Write comprehensive tests
- Use HTTPS for external APIs
- Implement graceful shutdown
- Document API endpoints

### DON'T ❌

- Hardcode credentials
- Expose internal errors to clients
- Use synchronous operations for I/O
- Ignore error handling
- Execute user input directly
- Store sensitive data in logs
- Use blocking operations
- Ignore security headers
- Skip input validation
- Use global state
- Mix business logic with routes
- Ignore performance optimization
- Skip health checks

---

## Resources

### Official Documentation
- [Express.js](https://expressjs.com/)
- [Node.js](https://nodejs.org/docs/)
- [Axios](https://axios-http.com/)

### Security
- [OWASP Node.js Security](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)
- [Helmet.js](https://helmetjs.github.io/)

### Testing
- [Jest](https://jestjs.io/)
- [Supertest](https://github.com/visionmedia/supertest)
- [Nock](https://github.com/nock/nock)

---

**Last Updated:** 2026-05-22  
**Version:** 2.0.0  
**Maintainer:** Operations Dashboard Team