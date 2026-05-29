---
name: backend-development
description: Node.js and Express backend development with API design, Turbonomic integration, security best practices, and performance optimization
---

# Backend Development Skill

Use this skill when developing backend APIs, integrating external services, implementing middleware, optimizing server performance, or working with the Turbonomic API.

## When to Use This Skill

- Creating or modifying API endpoints
- Integrating with Turbonomic API
- Implementing authentication and authorization
- Adding middleware for logging, validation, or security
- Optimizing backend performance
- Handling errors and implementing security measures
- Setting up server configuration

## Core Technologies

- Node.js (v18+)
- Express.js framework
- Axios for HTTP requests
- Winston for logging
- Jest for testing

## Key Principles

1. **RESTful API Design** - Follow REST conventions for endpoints
2. **Security First** - Validate inputs, sanitize data, use secure practices
3. **Error Handling** - Centralized error handling with proper status codes
4. **Performance** - Implement caching, compression, and connection pooling
5. **Testability** - Write testable, modular code

## Quick Reference

### Express Server Setup
```javascript
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/turbonomic', require('./routes/turbonomic'));

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error'
  });
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### API Endpoint Pattern
```javascript
const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');

router.post('/actions',
  // Validation
  body('turboHost').isURL(),
  body('turboUsername').notEmpty(),
  body('turboPassword').notEmpty(),
  
  // Handler
  async (req, res, next) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }
      
      const { turboHost, turboUsername, turboPassword } = req.body;
      const actions = await turbonomicService.getActions(
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

module.exports = router;
```

### Turbonomic API Integration
```javascript
const axios = require('axios');

class TurbonomicService {
  async getActions(host, username, password) {
    const auth = Buffer.from(`${username}:${password}`).toString('base64');
    
    const response = await axios.post(
      `${host}/api/v3/actions`,
      {
        actionStateList: ['PENDING_ACCEPT', 'RECOMMENDED']
      },
      {
        headers: {
          'Authorization': `Basic ${auth}`,
          'Content-Type': 'application/json'
        },
        httpsAgent: new https.Agent({
          rejectUnauthorized: false
        })
      }
    );
    
    return response.data;
  }
}

module.exports = new TurbonomicService();
```

## Common Patterns

### Error Handling
```javascript
// Custom error class
class ApiError extends Error {
  constructor(message, status = 500) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

// Async error wrapper
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Usage
router.get('/data', asyncHandler(async (req, res) => {
  const data = await fetchData();
  if (!data) {
    throw new ApiError('Data not found', 404);
  }
  res.json(data);
}));
```

### Request Validation
```javascript
const { body, param, query, validationResult } = require('express-validator');

const validateRequest = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  next();
};

router.post('/endpoint',
  body('email').isEmail(),
  body('age').isInt({ min: 0 }),
  validateRequest,
  handler
);
```

### Caching Strategy
```javascript
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 300 }); // 5 minutes

const cacheMiddleware = (duration) => (req, res, next) => {
  const key = req.originalUrl;
  const cached = cache.get(key);
  
  if (cached) {
    return res.json(cached);
  }
  
  res.originalJson = res.json;
  res.json = (data) => {
    cache.set(key, data, duration);
    res.originalJson(data);
  };
  
  next();
};
```

## File Organization
```
backend/src/
├── config/             # Configuration files
├── middleware/         # Custom middleware
├── routes/            # Route definitions
├── services/          # Business logic
├── utils/             # Helper functions
├── __tests__/         # Test files
└── server.js          # Entry point
```

## Security Best Practices

### Environment Variables
```javascript
// Use dotenv for configuration
require('dotenv').config();

const config = {
  port: process.env.PORT || 4000,
  nodeEnv: process.env.NODE_ENV || 'development',
  corsOrigin: process.env.CORS_ORIGIN || '*'
};
```

### Input Sanitization
```javascript
const sanitize = require('sanitize-html');

const sanitizeInput = (input) => {
  return sanitize(input, {
    allowedTags: [],
    allowedAttributes: {}
  });
};
```

### Rate Limiting
```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP'
});

app.use('/api/', limiter);
```

## Supporting Documentation

Refer to the following files in this skill folder for detailed guidance:
- `api-design.md` - RESTful API design patterns
- `turbonomic-integration.md` - Turbonomic API integration details
- `security.md` - Security best practices and implementation
- `performance.md` - Performance optimization strategies
- `testing.md` - Backend testing patterns

## Best Practices

### DO ✅
- Use environment variables for configuration
- Implement centralized error handling
- Validate and sanitize all inputs
- Use async/await for asynchronous operations
- Implement proper logging
- Use middleware for cross-cutting concerns
- Write comprehensive tests
- Document API endpoints

### DON'T ❌
- Expose sensitive data in responses
- Use synchronous operations in routes
- Ignore error handling
- Hardcode credentials or secrets
- Skip input validation
- Use `eval()` or execute user input
- Ignore security headers
- Leave debug code in production

## Health Checks

Always implement health check endpoints:
```javascript
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

app.get('/ready', async (req, res) => {
  // Check dependencies
  const checks = await Promise.all([
    checkDatabase(),
    checkExternalAPI()
  ]);
  
  const ready = checks.every(check => check.ok);
  res.status(ready ? 200 : 503).json({
    ready,
    checks
  });
});
```

## Resources

- [Express.js Documentation](https://expressjs.com/)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
- [REST API Design](https://restfulapi.net/)