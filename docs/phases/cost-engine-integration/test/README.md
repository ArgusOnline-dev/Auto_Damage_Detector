# Cost Engine Integration – Testing Notes

## Automated Integration Tests

A comprehensive test script (`test_cost_engine.py`) validates all testing requirements from the plan:

### Test Scenarios

1. **Happy Path**: Multiple damage types produce correct line items and totals
   - Verifies line items are generated correctly
   - Checks that all required fields are present
   - Validates totals calculation

2. **OEM vs. Used Toggle**: Same detections produce different totals
   - Tests with `use_oem_parts=true`
   - Tests with `use_oem_parts=false`
   - Verifies OEM total > Used total

3. **Unknown Combination Fallback**: Graceful handling of missing CSV entries
   - Tests with unknown part/damage combinations
   - Verifies fallback values are used
   - Ensures API doesn't crash

4. **Severity Overrides**: Frontend severity is respected
   - Tests with explicit severity overrides
   - Verifies backend respects user-provided severity
   - Validates severity appears in line items

### Running the Tests

```bash
# Make sure backend is running
python server.py start backend

# Run the tests
cd docs/phases/cost-engine-integration/test
python test_cost_engine.py
```

### Expected Results

All 4 test scenarios should pass:
- ✅ Happy path test
- ✅ OEM vs. used toggle test
- ✅ Unknown combination fallback test
- ✅ Severity override test

## Manual Testing

You can also use the existing integration script (`docs/phases/ml-model-training/test/test_two_stage_integration.py`) for quick validation:

1. Run `/infer` to obtain live detections.
2. Call `/estimate` twice:
   - With `use_oem_parts=true`
   - With `use_oem_parts=false`
3. Confirm the totals differ (OEM > used) and that severity fields reflect the backend's assignments.

## Future Unit Tests

For more targeted testing (future work):
- Test damage-to-CSV mapping (Stage damage → CSV damage type).
- Test part normalization (e.g., `front_bumper` → `Front bumper`).
- Test CSV lookup fallback when a combination is missing.
