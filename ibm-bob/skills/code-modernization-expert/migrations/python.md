# Python Modernization Guide

## Python 2 → Python 3 Migration

### Key Transformations

#### 1. Print Statements → Function
```python
# Before
print "Hello, World!"

# After
print("Hello, World!")
```

#### 2. Unicode Strings
```python
# Before
u"Hello, 世界"

# After
"Hello, 世界"  # Default in Python 3
```

#### 3. Dictionary Iteration
```python
# Before
for key, value in my_dict.iteritems():
    process(key, value)

# After
for key, value in my_dict.items():
    process(key, value)
```

#### 4. Import Changes
```python
# Before
import urllib
import ConfigParser

# After
import urllib.request
import configparser
```

#### 5. Division Operator
```python
# Before
result = 5 / 2  # Returns 2 in Python 2

# After
result = 5 // 2  # Integer division
result = 5 / 2   # Returns 2.5 in Python 3
```

### Modern Python Patterns (3.6+)

#### Type Hints
```python
# Before
def process_users(users):
    return [u for u in users if u.active]

# After
from typing import List

def process_users(users: List[User]) -> List[User]:
    return [u for u in users if u.active]

# Python 3.10+ with union types
def fetch_user(user_id: int) -> User | None:
    return db.get(user_id)
```

#### Dataclasses
```python
# Before
class User:
    def __init__(self, name, email, age=0):
        self.name = name
        self.email = email
        self.age = age

# After
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    age: int = 0
```

#### Pattern Matching (3.10+)
```python
# Before
def handle_response(response):
    if response['status'] == 'success':
        return response['data']
    elif response['status'] == 'error':
        raise APIError(response['message'])
    else:
        raise UnknownStatusError()

# After
def handle_response(response):
    match response:
        case {'status': 'success', 'data': data}:
            return data
        case {'status': 'error', 'message': msg}:
            raise APIError(msg)
        case _:
            raise UnknownStatusError()
```

#### Async/Await
```python
# Before (callbacks or threads)
def fetch_all_users(callback):
    def on_complete(result):
        callback(result)
    thread = Thread(target=_fetch, args=(on_complete,))
    thread.start()

# After
async def fetch_all_users() -> List[User]:
    async with aiohttp.ClientSession() as session:
        async with session.get('/api/users') as response:
            data = await response.json()
            return [User(**u) for u in data]
```

#### Context Managers
```python
# Before
f = open('data.txt')
try:
    data = f.read()
finally:
    f.close()

# After
with open('data.txt') as f:
    data = f.read()
```

#### F-strings
```python
# Before
message = "Hello, %s!" % name
message = "Hello, {}!".format(name)

# After
message = f"Hello, {name}!"
message = f"Total: ${price * quantity:.2f}"
```

## Migration Checklist

- [ ] Update print statements to function calls
- [ ] Remove u'' unicode string prefixes
- [ ] Change dict.iteritems() to dict.items()
- [ ] Update import statements (urllib, ConfigParser, etc.)
- [ ] Fix division operators (/ vs //)
- [ ] Add type hints to functions
- [ ] Convert classes to dataclasses where appropriate
- [ ] Replace old-style formatting with f-strings
- [ ] Use context managers for file operations
- [ ] Add async/await for concurrent operations
- [ ] Update requirements.txt with Python 3 compatible versions
- [ ] Run 2to3 tool for automated fixes
- [ ] Test thoroughly with Python 3 interpreter