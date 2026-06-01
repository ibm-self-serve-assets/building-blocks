# Testing Strategies for Legacy Code

## Characterization Testing

Capture existing behavior before refactoring, even if that behavior is buggy.

```python
class CharacterizationTest:
    """
    Characterization tests capture what code DOES,
    not what it SHOULD do. They're a safety net for refactoring.
    """

    def test_calculate_discount_captures_behavior(self):
        # Run legacy function with known inputs
        result = legacy_discount_calculator.calculate(
            customer_type='premium',
            order_total=100.00,
            items_count=5
        )

        # Assert actual behavior (even if "wrong")
        assert result == 17.50  # This is what it does

    def test_capture_edge_cases(self):
        # Document edge case behavior
        assert legacy_func(None) == ''      # Handles None
        assert legacy_func(-1) == 0         # Negative becomes zero
        assert legacy_func(999999) == 999   # Capped at 999
```

## Golden Master Testing

Capture production I/O pairs to validate new implementation.

```python
class GoldenMasterTestGenerator:
    """Generate tests from production traffic"""

    def __init__(self, legacy_system):
        self.legacy = legacy_system
        self.golden_masters = []

    def capture_production_traffic(self, duration_hours=24):
        """Record real inputs and outputs"""
        for request in self.production_traffic_stream():
            input_data = request.to_dict()
            output_data = self.legacy.process(request)

            self.golden_masters.append({
                'input': input_data,
                'expected_output': output_data.to_dict(),
                'timestamp': datetime.now()
            })

    def generate_test_file(self, output_path):
        """Generate pytest file from golden masters"""
        test_code = '''
import pytest
from system import ModernSystem

@pytest.mark.parametrize("input_data,expected", [
'''
        for gm in self.golden_masters:
            test_code += f"    ({gm['input']!r}, {gm['expected_output']!r}),\n"

        test_code += '''
])
def test_golden_master(input_data, expected, modern_system):
    result = modern_system.process(input_data)
    assert result == expected
'''
        Path(output_path).write_text(test_code)
```

## Approval Testing

Snapshot entire outputs for complex functions.

```python
import approvaltests

def test_report_generation():
    """Verify entire report structure"""
    report = legacy_report_generator.generate(
        start_date='2024-01-01',
        end_date='2024-01-31',
        department='sales'
    )

    # First run creates approved file
    # Subsequent runs compare against it
    approvaltests.verify(report)

def test_api_response_structure():
    """Verify entire JSON structure"""
    response = legacy_api.get_user_details(user_id=123)
    approvaltests.verify_as_json(response)
```

## Testing Workflow

1. **Before Migration:**
   - Generate characterization tests
   - Capture golden masters from production
   - Set up approval tests for complex outputs
   - Establish baseline test coverage

2. **During Migration:**
   - Run characterization tests after each change
   - Validate against golden masters
   - Update approval snapshots when behavior intentionally changes
   - Add new unit tests for modernized code

3. **After Migration:**
   - Verify all tests pass
   - Check test coverage increased
   - Remove characterization tests for fixed bugs
   - Keep golden master tests as regression suite

## Best Practices

- **Start with characterization tests** - Even for buggy behavior
- **Use golden masters for complex systems** - Capture real production data
- **Approval tests for large outputs** - Reports, API responses, etc.
- **Don't skip tests** - They're your safety net
- **Test edge cases** - Null, empty, negative, overflow
- **Run tests frequently** - After every small change