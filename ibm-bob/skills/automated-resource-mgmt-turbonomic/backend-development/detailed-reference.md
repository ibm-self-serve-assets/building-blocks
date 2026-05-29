# Backend Development - Detailed Reference

This file contains comprehensive reference material for backend development. Refer to SKILL.md for quick guidance and use this file for detailed examples and patterns.

## Express Server Architecture

### Complete Server Setup
```javascript
// server.js
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');

const app = express();

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"]
    }
  }
}));

// CORS configuration
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Compression
app.use(compression());

// Logging
app.use(morgan('combined'));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: 'Too many requests from this IP'
});
app.use('/api/', limiter);

// Routes
app.use('/api/turbonomic', require('./routes/turbonomic'));
app.use('/api/health', require('./routes/health'));

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  
  const status = err.status || 500;
  const message = err.message || 'Internal server error';
  
  res.status(status).json({
    error: message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;
```

## Turbonomic Integration

### Complete Service Implementation
```javascript
// services/turbonomicService.js
const axios = require('axios');
const https = require('https');
const NodeCache = require('node-cache');

class TurbonomicService {
  constructor() {
    this.cache = new NodeCache({ stdTTL: 300 }); // 5 minutes
  }

  createClient(host, username, password) {
    const auth = Buffer.from(`${username}:${password}`).toString('base64');
    
    return axios.create({
      baseURL: host,
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json'
      },
      httpsAgent: new https.Agent({
        rejectUnauthorized: false
      }),
      timeout: 30000
    });
  }

  async getEntities(host, username, password, types = []) {
    const cacheKey = `entities_${host}_${types.join('_')}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached) {
      return cached;
    }

    const client = this.createClient(host, username, password);
    
    try {
      const response = await client.post('/api/v3/search', {
        className: types.length > 0 ? types : undefined,
        environmentType: 'HYBRID'
      });
      
      const entities = response.data;
      this.cache.set(cacheKey, entities);
      
      return entities;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getPendingActions(host, username, password) {
    const cacheKey = `actions_${host}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached) {
      return cached;
    }

    const client = this.createClient(host, username, password);
    
    try {
      const response = await client.post('/api/v3/actions', {
        actionStateList: ['PENDING_ACCEPT', 'RECOMMENDED'],
        detailLevel: 'EXECUTION'
      });
      
      const actions = response.data;
      this.cache.set(cacheKey, actions);
      
      return actions;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getTargets(host, username, password) {
    const cacheKey = `targets_${host}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached) {
      return cached;
    }

    const client = this.createClient(host, username, password);
    
    try {
      const response = await client.get('/api/v3/targets');
      const targets = response.data;
      this.cache.set(cacheKey, targets);
      
      return targets;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  handleError(error) {
    if (error.response) {
      const status = error.response.status;
      const message = error.response.data?.message || error.message;
      
      if (status === 401) {
        return new Error('Invalid credentials');
      } else if (status === 403) {
        return new Error('Access forbidden');
      } else if (status === 404) {
        return new Error('Resource not found');
      } else if (status >= 500) {
        return new Error('Turbonomic server error');
      }
      
      return new Error(message);
    } else if (error.request) {
      return new Error('Unable to connect to Turbonomic server');
    }
    
    return error;
  }

  clearCache() {
    this.cache.flushAll();
  }
}

module.exports = new TurbonomicService();
```

### Route Implementation
```javascript
// routes/turbonomic.js
const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const turbonomicService = require('../services/turbonomicService');

// Validation middleware
const validateCredentials = [
  body('turboHost').isURL().withMessage('Invalid Turbonomic host URL'),
  body('turboUsername').notEmpty().withMessage('Username is required'),
  body('turboPassword').notEmpty().withMessage('Password is required')
];

const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  next();
};

// Get entities
router.post('/entities',
  validateCredentials,
  handleValidationErrors,
  async (req, res, next) => {
    try {
      const { turboHost, turboUsername, turboPassword, types } = req.body;
      
      const entities = await turbonomicService.getEntities(
        turboHost,
        turboUsername,
        turboPassword,
        types
      );
      
      res.json(entities);
    } catch (error) {
      next(error);
    }
  }
);

// Get pending actions
router.post('/actions',
  validateCredentials,
  handleValidationErrors,
  async (req, res, next) => {
    try {
      const { turboHost, turboUsername, turboPassword } = req.body;
      
      const actions = await turbonomicService.getPendingActions(
        turboHost,
        turboUsername,
        turboPassword
      );
      
      res.json(actions);
    } catch (error) {
      next(error);
    }
  }
);

// Get targets
router.post('/targets',
  validateCredentials,
  handleValidationErrors,
  async (req, res, next) => {
    try {
      const { turboHost, turboUsername, turboPassword } = req.body;
      
      const targets = await turbonomicService.getTargets(
        turboHost,
        turboUsername,
        turboPassword
      );
      
      res.json(targets);
    } catch (error) {
      next(error);
    }
  }
);

// Clear cache
router.post('/cache/clear',
  async (req, res) => {
    turbonomicService.clearCache();
    res.json({ message: 'Cache cleared successfully' });
  }
);

module.exports = router;
```

## Advanced Error Handling

### Custom Error Classes
```javascript
// utils/errors.js
class ApiError extends Error {
  constructor(message, status = 500, code = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

class ValidationError extends ApiError {
  constructor(message, errors = []) {
    super(message, 400, 'VALIDATION_ERROR');
    this.errors = errors;
  }
}

class AuthenticationError extends ApiError {
  constructor(message = 'Authentication failed') {
    super(message, 401, 'AUTH_ERROR');
  }
}

class NotFoundError extends ApiError {
  constructor(message = 'Resource not found') {
    super(message, 404, 'NOT_FOUND');
  }
}

module.exports = {
  ApiError,
  ValidationError,
  AuthenticationError,
  NotFoundError
};
```

### Error Handler Middleware
```javascript
// middleware/errorHandler.js
const { ApiError } = require('../utils/errors');

const errorHandler = (err, req, res, next) => {
  // Log error
  console.error({
    message: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    timestamp: new Date().toISOString()
  });

  // Handle known errors
  if (err instanceof ApiError) {
    return res.status(err.status).json({
      error: err.message,
      code: err.code,
      ...(err.errors && { errors: err.errors })
    });
  }

  // Handle validation errors
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: 'Validation failed',
      details: err.errors
    });
  }

  // Handle JWT errors
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({
      error: 'Invalid token'
    });
  }

  // Default error
  res.status(500).json({
    error: 'Internal server error',
    ...(process.env.NODE_ENV === 'development' && { 
      message: err.message,
      stack: err.stack 
    })
  });
};

module.exports = errorHandler;
```

## Security Implementations

### Input Sanitization
```javascript
// middleware/sanitization.js
const sanitizeHtml = require('sanitize-html');

const sanitizeInput = (input) => {
  if (typeof input === 'string') {
    return sanitizeHtml(input, {
      allowedTags: [],
      allowedAttributes: {}
    });
  }
  
  if (Array.isArray(input)) {
    return input.map(sanitizeInput);
  }
  
  if (typeof input === 'object' && input !== null) {
    const sanitized = {};
    for (const [key, value] of Object.entries(input)) {
      sanitized[key] = sanitizeInput(value);
    }
    return sanitized;
  }
  
  return input;
};

const sanitizationMiddleware = (req, res, next) => {
  if (req.body) {
    req.body = sanitizeInput(req.body);
  }
  if (req.query) {
    req.query = sanitizeInput(req.query);
  }
  if (req.params) {
    req.params = sanitizeInput(req.params);
  }
  next();
};

module.exports = { sanitizeInput, sanitizationMiddleware };
```

### Request Logging
```javascript
// middleware/requestLogger.js
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

const requestLogger = (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    
    logger.info({
      method: req.method,
      url: req.url,
      status: res.statusCode,
      duration: `${duration}ms`,
      ip: req.ip,
      userAgent: req.get('user-agent')
    });
  });
  
  next();
};

module.exports = { logger, requestLogger };
```

## Testing Patterns

### API Endpoint Tests
```javascript
// __tests__/turbonomic.test.js
const request = require('supertest');
const app = require('../src/server');
const turbonomicService = require('../src/services/turbonomicService');

jest.mock('../src/services/turbonomicService');

describe('Turbonomic API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/turbonomic/entities', () => {
    it('returns entities with valid credentials', async () => {
      const mockEntities = [
        { id: '1', className: 'VirtualMachine' },
        { id: '2', className: 'Container' }
      ];
      
      turbonomicService.getEntities.mockResolvedValue(mockEntities);
      
      const response = await request(app)
        .post('/api/turbonomic/entities')
        .send({
          turboHost: 'https://test.com',
          turboUsername: 'admin',
          turboPassword: 'password'
        });
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockEntities);
      expect(turbonomicService.getEntities).toHaveBeenCalledWith(
        'https://test.com',
        'admin',
        'password',
        undefined
      );
    });

    it('returns 400 with missing credentials', async () => {
      const response = await request(app)
        .post('/api/turbonomic/entities')
        .send({});
      
      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('errors');
    });

    it('handles service errors', async () => {
      turbonomicService.getEntities.mockRejectedValue(
        new Error('Connection failed')
      );
      
      const response = await request(app)
        .post('/api/turbonomic/entities')
        .send({
          turboHost: 'https://test.com',
          turboUsername: 'admin',
          turboPassword: 'password'
        });
      
      expect(response.status).toBe(500);
    });
  });
});
```

For the complete original guide with all sections, see the archived `backend-guide.md` file.