# Seam-Based Refactoring Pattern

Identify "seams" (points where behavior can be changed) to enable testing and gradual refactoring.

## When to Use
- Low or zero test coverage
- Tightly coupled legacy code
- Need to add tests before refactoring
- Working with untestable code

## Seam Types

| Type | Description | How to Exploit |
|------|-------------|----------------|
| Object | Object creation points | Dependency injection |
| Method | Overridable method calls | Extract and override |
| Link | Runtime binding | Interface injection |

## Implementation Steps

### Phase 1: Find Seams
1. Identify natural boundaries
2. Look for method calls, object creation, data sources
3. Map dependencies crossing seams
4. Prioritize by risk and value

### Phase 2: Break Dependencies
1. Extract interfaces at seam boundaries
2. Inject dependencies instead of creating them
3. Replace static calls with instance methods
4. Isolate external system calls

### Phase 3: Add Tests
1. Write characterization tests
2. Add unit tests using test doubles at seams
3. Create integration tests for critical paths

### Phase 4: Refactor
1. Make small, incremental changes
2. Run tests after each change
3. Commit frequently

## Example

```python
# Before: Hard dependency
class OrderProcessor:
    def process_order(self, order):
        db = MySQLConnection('prod_db')  # Hard-coded!
        result = db.execute(f"INSERT INTO orders VALUES {order}")
        return result

# After: Seam created
class OrderProcessor:
    def __init__(self, db_connection=None):
        self.db = db_connection or MySQLConnection('prod_db')
    
    def process_order(self, order):
        result = self.db.execute(f"INSERT INTO orders VALUES {order}")
        return result

# Now testable
def test_order_processing():
    mock_db = MockConnection()
    processor = OrderProcessor(mock_db)
    result = processor.process_order(test_order)
    assert result.success