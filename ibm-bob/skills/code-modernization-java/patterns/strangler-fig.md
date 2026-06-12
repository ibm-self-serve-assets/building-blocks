# Strangler Fig Pattern

Incrementally replace legacy systems by building new functionality alongside the old, gradually routing traffic until legacy code can be retired.

## Implementation Steps

### Phase 1: Intercept
1. Add routing layer/facade in front of legacy system
2. All requests pass through facade to legacy
3. No behavior change - establish baseline
4. Add comprehensive logging and monitoring

### Phase 2: Strangle
For each module to modernize:
1. Build new implementation alongside legacy
2. Route subset of traffic to new implementation (feature flags)
3. Validate behavior matches (shadow testing)
4. Gradually increase traffic percentage (1% → 5% → 25% → 50% → 100%)
5. Monitor metrics and errors continuously
6. Once 100% routed, mark legacy for removal

### Phase 3: Remove
1. Verify no traffic to legacy module
2. Remove routing rules
3. Delete legacy code
4. Clean up dependencies
5. Update documentation

## Example Implementation

```python
class UserServiceFacade:
    """Strangler facade for gradual user service migration"""
    
    def __init__(self, feature_flags, metrics):
        self.flags = feature_flags
        self.metrics = metrics
        self.legacy = LegacyUserService()
        self.modern = ModernUserService()
    
    def get_user(self, user_id):
        # Check feature flag for gradual rollout
        if self.flags.use_modern_user_service(user_id):
            try:
                result = self.modern.fetch(user_id)
                
                # Shadow comparison in non-blocking way
                self._compare_async(user_id, result)
                
                self.metrics.increment('modern_service_success')
                return result
                
            except Exception as e:
                self.metrics.increment('modern_service_failure')
                self._log_fallback(user_id, e)
                # Automatic fallback to legacy
                return self.legacy.fetch(user_id)
        
        self.metrics.increment('legacy_service_used')
        return self.legacy.fetch(user_id)
    
    def _compare_async(self, user_id, modern_result):
        """Compare modern vs legacy results without blocking"""
        asyncio.create_task(
            self._shadow_test(user_id, modern_result)
        )
```

## Key Success Factors

- Feature toggles for gradual rollout
- Comprehensive logging and monitoring
- Automated rollback capability
- Clear success metrics for each phase
- Non-blocking shadow testing
- Automatic fallback on errors