# Parallel Run (Shadow Testing) Pattern

Run new implementation alongside legacy, compare results without affecting production.

## When to Use
- Mission-critical systems
- Financial applications
- Healthcare systems
- High-risk migrations

## Implementation Steps

### Setup
1. Deploy new implementation alongside old
2. Configure traffic mirroring
3. Set up comparison infrastructure
4. Define acceptable differences

### Execution
For each request:
1. Process through legacy system (primary)
2. Mirror to new system (async, non-blocking)
3. Compare outputs
4. Log discrepancies
5. Return legacy result to user

### Analysis
1. Review comparison logs daily
2. Categorize discrepancies:
   - Bug in new code (fix required)
   - Bug in legacy code (expected)
   - Acceptable variation (document)
3. Track convergence metrics

### Cutover
1. When discrepancy rate < threshold
2. Switch primary to new system
3. Keep legacy as fallback
4. Monitor for 1-2 weeks
5. Decommission legacy

## Example

```python
class ShadowTestingService:
    def __init__(self, legacy, modern, comparator):
        self.legacy = legacy
        self.modern = modern
        self.comparator = comparator
        self.metrics = MetricsCollector()
    
    def execute(self, request):
        # Always use legacy for actual response
        legacy_result = self.legacy.process(request)
        
        # Run modern in parallel (non-blocking)
        asyncio.create_task(
            self._shadow_run(request, legacy_result)
        )
        
        return legacy_result
    
    async def _shadow_run(self, request, legacy_result):
        try:
            modern_result = await self.modern.process(request)
            comparison = self.comparator.compare(legacy_result, modern_result)
            
            if comparison.matches:
                self.metrics.record_match()
            else:
                self.metrics.record_mismatch(comparison.differences)
                self._alert_team(request, comparison)
        except Exception as e:
            self.metrics.record_error(e)