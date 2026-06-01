# Ruby Modernization (2 → 3)

## Key Transformations

### 1. Keyword Arguments
```ruby
# Before (Ruby 2)
def create_user(name, email, role = 'user', active = true)
  # ...
end
create_user('Alice', 'alice@example.com', 'admin', false)

# After (Ruby 3 - keyword arguments required)
def create_user(name:, email:, role: 'user', active: true)
  # ...
end
create_user(name: 'Alice', email: 'alice@example.com', role: 'admin', active: false)
```

### 2. Numbered Parameters
```ruby
# Before (Ruby 2)
[1, 2, 3].map { |n| n * 2 }

# After (Ruby 3)
[1, 2, 3].map { _1 * 2 }

# Multiple parameters
users.map { [_1.name, _2.email] }
```

### 3. Pattern Matching
```ruby
# Before (Ruby 2)
case status
when 'pending'
  'Waiting'
when 'approved'
  'Done'
else
  'Unknown'
end

# After (Ruby 3)
case status
in 'pending'
  'Waiting'
in 'approved'
  'Done'
else
  'Unknown'
end

# Advanced pattern matching
case user
in { name:, email:, role: 'admin' }
  "Admin: #{name}"
in { name:, email: }
  "User: #{name}"
end
```

### 4. Endless Method Definition
```ruby
# Before (Ruby 2)
def double(n)
  n * 2
end

# After (Ruby 3)
def double(n) = n * 2
```

### 5. Rightward Assignment
```ruby
# Before (Ruby 2)
result = calculate_total(items)
puts result

# After (Ruby 3)
calculate_total(items) => result
puts result
```

### 6. Hash Shorthand
```ruby
# Before (Ruby 2)
name = 'Alice'
email = 'alice@example.com'
user = { name: name, email: email }

# After (Ruby 3.1+)
name = 'Alice'
email = 'alice@example.com'
user = { name:, email: }
```

### 7. Fiber Scheduler (Async)
```ruby
# Before (Ruby 2 - threads)
threads = urls.map do |url|
  Thread.new { fetch(url) }
end
results = threads.map(&:value)

# After (Ruby 3 - fibers with scheduler)
require 'async'

Async do
  results = urls.map do |url|
    Async { fetch(url) }
  end.map(&:wait)
end
```

### 8. Type Signatures (RBS)
```ruby
# Create .rbs file for type definitions
# user.rbs
class User
  attr_reader name: String
  attr_reader email: String
  
  def initialize: (name: String, email: String) -> void
  def valid?: () -> bool
end
```

### 9. Gem Updates
```ruby
# Gemfile - Update to Ruby 3 compatible versions
ruby '3.2.0'

gem 'rails', '~> 7.0'
gem 'puma', '~> 6.0'
gem 'pg', '~> 1.4'
```

## Breaking Changes to Address

### Keyword Arguments Separation
```ruby
# Ruby 2 (works)
def foo(options)
  # ...
end
foo(a: 1, b: 2)

# Ruby 3 (error - must be explicit)
def foo(**options)
  # ...
end
foo(a: 1, b: 2)
```

### Hash to Keyword Arguments
```ruby
# Ruby 2 (automatic conversion)
def foo(a:, b:)
  # ...
end
options = { a: 1, b: 2 }
foo(options)  # Works in Ruby 2

# Ruby 3 (must use double splat)
foo(**options)  # Required in Ruby 3
```

## Migration Checklist
- [ ] Update Ruby version to 3.x
- [ ] Convert positional args to keyword args
- [ ] Fix keyword argument separation issues
- [ ] Use numbered parameters where appropriate
- [ ] Add pattern matching for complex conditionals
- [ ] Use endless method definitions for simple methods
- [ ] Update Gemfile with Ruby 3 compatible versions
- [ ] Run bundle update
- [ ] Consider adding RBS type signatures
- [ ] Test with Ruby 3 interpreter
- [ ] Update CI/CD to Ruby 3
- [ ] Review deprecation warnings