# Java Modernization (8 → 17/21)

## Key Transformations

### 1. javax → jakarta namespace
```java
// Before
import javax.persistence.Entity;
import javax.validation.constraints.NotNull;

// After
import jakarta.persistence.Entity;
import jakarta.validation.constraints.NotNull;
```

### 2. Date/Time API
```java
// Before
Date date = new Date();
SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");

// After
LocalDate date = LocalDate.now();
String formatted = date.format(DateTimeFormatter.ISO_LOCAL_DATE);
```

### 3. Optional for null handling
```java
// Before
User user = userRepository.findById(id);
if (user != null) {
    sendEmail(user.getEmail());
}

// After
userRepository.findById(id)
    .map(User::getEmail)
    .ifPresent(this::sendEmail);
```

### 4. Pattern Matching
```java
// Before
if (shape instanceof Circle) {
    Circle circle = (Circle) shape;
    return circle.radius() * Math.PI;
}

// After
if (shape instanceof Circle circle) {
    return circle.radius() * Math.PI;
}
```

### 5. Records
```java
// Before (50+ lines)
public class UserDto {
    private final String name;
    private final String email;
    // constructor, getters, equals, hashCode, toString...
}

// After (1 line)
public record UserDto(String name, String email) {}
```

### 6. Text Blocks
```java
// Before
String sql = "SELECT u.id, u.name\n" +
             "FROM users u\n" +
             "WHERE u.status = 'active'";

// After
String sql = """
    SELECT u.id, u.name
    FROM users u
    WHERE u.status = 'active'
    """;
```

### 7. Switch Expressions
```java
// Before
String result;
switch (status) {
    case PENDING: result = "Waiting"; break;
    case APPROVED: result = "Done"; break;
    default: result = "Unknown";
}

// After
String result = switch (status) {
    case PENDING -> "Waiting";
    case APPROVED -> "Done";
    default -> "Unknown";
};
```

## Migration Checklist
- [ ] Update javax.* to jakarta.*
- [ ] Replace Date with java.time.*
- [ ] Add Optional for null handling
- [ ] Use pattern matching for instanceof
- [ ] Convert POJOs to Records
- [ ] Use text blocks for multi-line strings
- [ ] Replace old switch with expressions
- [ ] Update Spring Boot 2.x to 3.x
- [ ] Test with Java 17/21 compiler