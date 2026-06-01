# PHP Modernization (5 → 8)

## Key Transformations

### 1. Constructor Property Promotion
```php
// Before (PHP 5)
class User {
    private $name;
    private $email;
    
    public function __construct($name, $email) {
        $this->name = $name;
        $this->email = $email;
    }
}

// After (PHP 8)
class User {
    public function __construct(
        private string $name,
        private string $email
    ) {}
}
```

### 2. Type Declarations
```php
// Before (PHP 5)
function calculateTotal($items) {
    $total = 0;
    foreach ($items as $item) {
        $total += $item;
    }
    return $total;
}

// After (PHP 8)
function calculateTotal(array $items): float {
    $total = 0.0;
    foreach ($items as $item) {
        $total += $item;
    }
    return $total;
}
```

### 3. Null Coalescing & Nullsafe Operator
```php
// Before (PHP 5)
$username = isset($_GET['user']) ? $_GET['user'] : 'guest';
$country = null;
if ($user !== null && $user->getAddress() !== null) {
    $country = $user->getAddress()->getCountry();
}

// After (PHP 8)
$username = $_GET['user'] ?? 'guest';
$country = $user?->getAddress()?->getCountry();
```

### 4. Match Expression
```php
// Before (PHP 5)
switch ($status) {
    case 'pending':
        $message = 'Waiting';
        break;
    case 'approved':
        $message = 'Done';
        break;
    default:
        $message = 'Unknown';
}

// After (PHP 8)
$message = match($status) {
    'pending' => 'Waiting',
    'approved' => 'Done',
    default => 'Unknown'
};
```

### 5. Named Arguments
```php
// Before (PHP 5)
function createUser($name, $email, $role = 'user', $active = true) {
    // ...
}
createUser('Alice', 'alice@example.com', 'user', false);

// After (PHP 8)
createUser(
    name: 'Alice',
    email: 'alice@example.com',
    active: false
);
```

### 6. Attributes (Annotations)
```php
// Before (PHP 5 - DocBlock)
/**
 * @Route("/api/users")
 */
class UserController {
    /**
     * @Get
     * @Auth("admin")
     */
    public function index() {}
}

// After (PHP 8 - Attributes)
#[Route("/api/users")]
class UserController {
    #[Get]
    #[Auth("admin")]
    public function index() {}
}
```

### 7. Union Types
```php
// Before (PHP 5)
/**
 * @param int|string $id
 * @return User|null
 */
function findUser($id) {
    // ...
}

// After (PHP 8)
function findUser(int|string $id): ?User {
    // ...
}
```

### 8. Arrow Functions
```php
// Before (PHP 5)
$doubled = array_map(function($n) {
    return $n * 2;
}, $numbers);

// After (PHP 8)
$doubled = array_map(fn($n) => $n * 2, $numbers);
```

## Migration Checklist
- [ ] Update PHP version to 8.x
- [ ] Add type declarations to functions
- [ ] Use constructor property promotion
- [ ] Replace isset() with null coalescing (??)
- [ ] Use nullsafe operator (?->)
- [ ] Convert switch to match expressions
- [ ] Add named arguments where helpful
- [ ] Replace DocBlock annotations with attributes
- [ ] Use union types
- [ ] Replace closures with arrow functions
- [ ] Update composer.json dependencies
- [ ] Run rector for automated fixes
- [ ] Test thoroughly with PHP 8