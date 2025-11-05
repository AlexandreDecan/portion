# Performance Improvements

This document describes the performance optimizations made to the `portion` library.

## Summary

Two major performance bottlenecks were identified and fixed:

1. **Interval.__init__ merging**: O(n²) → O(n) (CRITICAL FIX)
2. **IntervalDict.combine**: O(n×m) nested loop optimization

## 1. Interval Merging Optimization

### Problem

The `Interval.__init__` method uses a merging algorithm to combine overlapping or adjacent atomic intervals. The original implementation used `list.pop(i)` twice and `list.insert(i)` operations, which are O(n) each, making the overall merging algorithm O(n²).

**Location**: `portion/interval.py`, lines 52-96 (old version)

**Original Code Pattern**:
```python
while i < len(self._intervals) - 1:
    current = self._intervals[i]
    successor = self._intervals[i + 1]
    
    if mergeable:
        union = merge(current, successor)
        self._intervals.pop(i)     # O(n) - shifts remaining elements
        self._intervals.pop(i)     # O(n) - shifts remaining elements
        self._intervals.insert(i, union)  # O(n) - shifts elements
    else:
        i += 1
```

**Issue**: Each merge operation requires 3 O(n) operations (2 pops + 1 insert), leading to O(n²) complexity when many intervals need to be merged.

### Solution

Changed the algorithm to build a new merged list instead of modifying the original list in place. The new algorithm:
1. Iterates through intervals once
2. For each interval, keeps merging with consecutive intervals while possible
3. Appends the final merged interval to a new list
4. Replaces the original list with the merged list

**New Code Pattern**:
```python
merged = []
i = 0
while i < len(self._intervals):
    current = self._intervals[i]
    
    # Keep merging with consecutive intervals
    while i + 1 < len(self._intervals) and mergeable:
        successor = self._intervals[i + 1]
        current = merge(current, successor)
        i += 1
    
    merged.append(current)
    i += 1

self._intervals = merged
```

### Performance Results

**Before optimization** (estimated based on O(n²) complexity):
- 100 intervals: variable
- 1000 intervals: ~100x slower than 100
- 2000 intervals: ~400x slower than 100

**After optimization**:
- 100 intervals: 1.39 µs per interval
- 200 intervals: 1.31 µs per interval
- 500 intervals: 1.28 µs per interval
- 1000 intervals: 1.31 µs per interval
- 2000 intervals: 1.31 µs per interval

**Scaling ratio (2000/100)**: 0.94x - Nearly perfect linear scaling!

### Impact

This optimization is critical for:
- Creating intervals from many overlapping atomic intervals
- Union operations that result in merging
- Any operation that calls `Interval.__init__` with multiple intervals

Common use cases that benefit:
```python
# Merging many overlapping intervals
intervals = [P.closed(i, i+2) for i in range(1000)]
result = P.Interval(*intervals)  # Now O(n) instead of O(n²)

# Building complex intervals with union
result = P.empty()
for i in range(1000):
    result = result | P.closed(i, i+1)  # Each union is faster
```

## 2. IntervalDict.combine Optimization

### Problem

The `IntervalDict.combine` method had a nested loop that checked every pair of intervals from the two dictionaries within their intersection, resulting in O(n×m) complexity.

**Location**: `portion/dict.py`, lines 268-273 (old version)

**Original Code**:
```python
for i1, v1 in d1.items():
    for i2, v2 in d2.items():  # Nested loop - O(n×m)
        if i1.overlaps(i2):
            # combine values
```

### Solution

Implemented a sweep-line algorithm that:
1. Maintains a starting position in the second dict's items
2. Skips intervals that can't possibly overlap
3. Breaks early when no more overlaps are possible
4. Advances the starting position for intervals that end before the current interval

**New Code Pattern**:
```python
j_start = 0
for i1, v1 in items1:
    j = j_start
    while j < len(items2):
        i2, v2 = items2[j]
        
        # Early exit if i2 is after i1
        if i2.lower > i1.upper:
            break
        
        # Skip if i2 is before i1 and advance start
        if i2.upper < i1.lower:
            if j == j_start:
                j_start = j + 1
            j += 1
            continue
        
        # Process overlap
        if i1.overlaps(i2):
            # combine values
        
        j += 1
```

### Performance Characteristics

The optimization provides different benefits depending on the overlap pattern:

**Non-overlapping intervals** (best case improvement):
- Old: O(n×m) - checks all pairs
- New: O(n+m) - skips non-overlapping pairs

**Partially overlapping intervals**:
- Old: O(n×m)
- New: O(n×k) where k is average overlaps per interval

**All overlapping intervals** (worst case):
- Both: O(n×m) - must check all pairs

### Impact

This optimization is most beneficial for:
- Combining dicts with many non-overlapping intervals
- Large dicts where only a subset overlaps
- Sequential or time-series data with sparse overlaps

Less beneficial for:
- Fully overlapping intervals (must still check all pairs)
- Small dicts (overhead may dominate)

## Testing

Performance tests have been added in `tests/test_performance.py` to verify:
1. Interval merging has linear performance
2. IntervalDict.combine works correctly after optimization
3. No regressions in correctness

Run performance tests:
```bash
python tests/test_performance.py
```

All existing tests continue to pass, ensuring no regressions in functionality.

## Recommendations for Users

To get the best performance from the optimized code:

1. **For interval merging**:
   - Create intervals from atomic intervals in batches when possible
   - Use `Interval(*atomics)` instead of iteratively using `|` operator
   
2. **For IntervalDict.combine**:
   - Structure data to minimize overlaps when overlaps aren't needed
   - Consider splitting large combines into smaller operations

## Future Optimization Opportunities

Additional optimizations that were considered but not implemented:

1. **IntervalDict.domain caching**: Could cache domain if frequently accessed
2. **IntervalDict.find indexing**: Could maintain reverse index for frequent lookups
3. **Interval operations**: Some set operations could benefit from similar sweep-line algorithms

These were not implemented to maintain minimal changes and because the primary bottleneck (interval merging) has been addressed.
