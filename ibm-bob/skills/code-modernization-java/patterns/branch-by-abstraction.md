# Branch by Abstraction Pattern

Create abstraction layer, implement new version behind it, then switch implementations.

## When to Use
- Internal library/module modernization
- Database access layer migrations
- Third-party dependency upgrades
- Algorithm replacements

## Implementation Steps

### Phase 1: Abstract
1. Identify boundary of code to modernize
2. Create interface representing current behavior
3. Wrap legacy code with abstraction
4. Update all callers to use abstraction
5. Verify no behavior change

### Phase 2: Implement
1. Create new implementation behind abstraction
2. Write tests for new implementation
3. Ensure both pass same test suite

### Phase 3: Switch
1. Use feature flags for controlled rollout
2. Gradually switch callers to new implementation
3. Monitor for regressions

### Phase 4: Clean
1. Remove legacy implementation
2. Optionally remove abstraction if no longer needed

## Example

```python
# Phase 1: Create abstraction
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount, card_info):
        pass

# Wrap legacy
class LegacyPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount, card_info):
        return legacy_payment_system.charge(amount, card_info)

# Phase 2: New implementation
class ModernPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount, card_info):
        return stripe_api.create_charge(amount=amount, source=card_info.token)

# Phase 3: Switch with feature flag
class PaymentService:
    def __init__(self, feature_flags):
        self.processor = (ModernPaymentProcessor() 
                         if feature_flags.use_modern_payments() 
                         else LegacyPaymentProcessor())
    
    def process(self, amount, card_info):
        return self.processor.process_payment(amount, card_info)