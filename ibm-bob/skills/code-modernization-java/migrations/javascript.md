# JavaScript Modernization (ES5 → ES6+)

## Key Transformations

### 1. var → let/const
```javascript
// Before
var name = "Alice";
var count = 0;

// After
const name = "Alice";  // Immutable
let count = 0;         // Mutable
```

### 2. Callbacks → Async/Await
```javascript
// Before
getUserData(userId, function(err, user) {
    if (err) return handleError(err);
    getOrders(user.id, function(err, orders) {
        if (err) return handleError(err);
        displayResult(orders);
    });
});

// After
async function processUser(userId) {
    try {
        const user = await getUserData(userId);
        const orders = await getOrders(user.id);
        displayResult(orders);
    } catch (err) {
        handleError(err);
    }
}
```

### 3. Arrow Functions
```javascript
// Before
var doubled = numbers.map(function(n) {
    return n * 2;
});

// After
const doubled = numbers.map(n => n * 2);
```

### 4. Template Literals
```javascript
// Before
var message = "Hello, " + name + "! You have " + count + " messages.";

// After
const message = `Hello, ${name}! You have ${count} messages.`;
```

### 5. Destructuring
```javascript
// Before
var name = user.name;
var email = user.email;

// After
const { name, email } = user;
```

### 6. Spread Operator
```javascript
// Before
var combined = arr1.concat(arr2);

// After
const combined = [...arr1, ...arr2];
const merged = { ...defaults, ...userSettings };
```

### 7. Classes
```javascript
// Before (Prototypes)
function User(name, email) {
    this.name = name;
    this.email = email;
}
User.prototype.greet = function() {
    return "Hello, " + this.name;
};

// After
class User {
    constructor(name, email) {
        this.name = name;
        this.email = email;
    }
    
    greet() {
        return `Hello, ${this.name}`;
    }
}
```

### 8. Modules
```javascript
// Before (CommonJS)
var express = require('express');
module.exports = router;

// After (ES Modules)
import express from 'express';
export default router;
```

## Migration Checklist
- [ ] Replace var with let/const
- [ ] Convert callbacks to async/await
- [ ] Use arrow functions
- [ ] Replace string concatenation with template literals
- [ ] Add destructuring where appropriate
- [ ] Use spread operator for arrays/objects
- [ ] Convert prototypes to classes
- [ ] Migrate to ES modules (import/export)
- [ ] Update package.json with "type": "module"
- [ ] Test with modern JavaScript runtime