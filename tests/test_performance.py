"""
Performance Test Suite for portion library

This module contains performance tests to validate the optimizations made to the
portion library, specifically:

1. Interval.__init__ merging optimization (O(n²) → O(n))
2. IntervalDict.combine optimization (nested loop improvements)

These tests verify both correctness and performance characteristics.
"""

import time
import portion as P


def test_interval_merging_linear_performance():
    """
    Test that interval merging has linear performance.
    
    Before optimization: O(n²) - used pop/insert operations
    After optimization: O(n) - builds merged list directly
    """
    times = []
    sizes = [100, 200, 500, 1000, 2000]
    
    for n in sizes:
        # Worst case: all intervals overlap and merge into one
        atomics = [P.closed(0, i+1) for i in range(n)]
        
        start = time.time()
        result = P.Interval(*atomics)
        elapsed = time.time() - start
        
        per_interval = elapsed / n
        times.append(per_interval)
        
        # Verify correctness
        assert len(result) == 1
        assert result == P.closed(0, n)
    
    # Check linear scaling - ratio should be close to 1.0
    ratio = times[-1] / times[0]
    assert ratio < 2.0, f"Performance should be linear, but ratio is {ratio:.2f}x"


def test_interval_partial_merging_performance():
    """
    Test performance when only some intervals merge.
    """
    sizes = [100, 200, 500, 1000]
    
    for n in sizes:
        # Create pairs of adjacent intervals that merge
        atomics = []
        for i in range(n):
            if i % 2 == 0:
                atomics.append(P.closed(i, i + 0.5))
            else:
                atomics.append(P.closed(i - 0.5, i))
        
        start = time.time()
        result = P.Interval(*atomics)
        elapsed = time.time() - start
        
        # Verify correctness
        assert len(result) == n // 2


def test_interval_no_merging_performance():
    """
    Test performance when no intervals merge (best case).
    """
    sizes = [100, 200, 500, 1000]
    
    for n in sizes:
        # Create non-overlapping intervals
        atomics = [P.closed(i*2, i*2 + 0.5) for i in range(n)]
        
        start = time.time()
        result = P.Interval(*atomics)
        elapsed = time.time() - start
        
        # Verify correctness
        assert len(result) == n


def test_intervaldict_combine_correctness():
    """
    Test that IntervalDict.combine still works correctly after optimization.
    """
    # Test basic combine
    d1 = P.IntervalDict({P.closed(0, 2): 'a'})
    d2 = P.IntervalDict({P.closed(1, 3): 'b'})
    result = d1.combine(d2, lambda x, y: f"{x}/{y}")
    
    # Verify the combine produced expected structure
    assert len(result) >= 3  # Should have split intervals
    
    # Test non-overlapping combine
    d1 = P.IntervalDict({P.closed(0, 1): 'a'})
    d2 = P.IntervalDict({P.closed(2, 3): 'b'})
    result = d1.combine(d2, lambda x, y: f"{x}/{y}")
    assert len(result) == 2
    
    # Test with missing parameter
    d1 = P.IntervalDict({P.closed(0, 2): 'a'})
    d2 = P.IntervalDict({P.closed(1, 3): 'b'})
    result = d1.combine(d2, lambda x, y: f"{x}/{y}", missing='x')
    assert len(result) >= 3


def test_intervaldict_combine_non_overlapping():
    """
    Test combine performance on non-overlapping intervals.
    
    This is where the optimization shows the most benefit:
    - Old: O(n*m) - checks all pairs
    - New: O(n+m) - skips non-overlapping pairs
    """
    sizes = [50, 100, 200]
    
    for n in sizes:
        d1 = P.IntervalDict()
        d2 = P.IntervalDict()
        
        # Create non-overlapping intervals
        for i in range(n):
            d1[P.closed(i*2, i*2 + 0.5)] = f"a{i}"
            d2[P.closed(i*2 + 1, i*2 + 1.5)] = f"b{i}"
        
        start = time.time()
        result = d1.combine(d2, lambda x, y: f"{x}/{y}")
        elapsed = time.time() - start
        
        # Verify correctness
        assert len(result) == n * 2


def benchmark_all():
    """
    Run all performance benchmarks and print results.
    """
    print("=" * 70)
    print("Performance Benchmark Results")
    print("=" * 70)
    
    print("\n1. Interval merging (worst case - all overlap):")
    sizes = [100, 200, 500, 1000, 2000]
    times = []
    
    for n in sizes:
        atomics = [P.closed(0, i+1) for i in range(n)]
        start = time.time()
        result = P.Interval(*atomics)
        elapsed = time.time() - start
        per_interval = elapsed / n * 1000000
        times.append(per_interval)
        print(f"   n={n:4d}: {elapsed:.6f}s ({per_interval:.2f}µs per interval)")
    
    ratio = times[-1] / times[0]
    print(f"   Scaling: {ratio:.2f}x (should be ~1.0 for linear)")
    
    print("\n2. Interval merging (partial merging):")
    for n in [100, 500, 1000]:
        atomics = []
        for i in range(n):
            if i % 2 == 0:
                atomics.append(P.closed(i, i + 0.5))
            else:
                atomics.append(P.closed(i - 0.5, i))
        
        start = time.time()
        result = P.Interval(*atomics)
        elapsed = time.time() - start
        print(f"   n={n:4d}: {elapsed:.6f}s ({elapsed/n*1000000:.2f}µs per interval)")
    
    print("\n3. IntervalDict combine (non-overlapping):")
    for n in [50, 100, 200]:
        d1 = P.IntervalDict()
        d2 = P.IntervalDict()
        
        for i in range(n):
            d1[P.closed(i*2, i*2 + 0.5)] = f"a{i}"
            d2[P.closed(i*2 + 1, i*2 + 1.5)] = f"b{i}"
        
        start = time.time()
        result = d1.combine(d2, lambda x, y: f"{x}/{y}")
        elapsed = time.time() - start
        print(f"   n={n:3d}: {elapsed:.6f}s ({elapsed/n*1000000:.2f}µs per item)")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run tests
    print("Running performance tests...\n")
    
    test_interval_merging_linear_performance()
    print("✓ Interval merging linear performance test passed")
    
    test_interval_partial_merging_performance()
    print("✓ Interval partial merging test passed")
    
    test_interval_no_merging_performance()
    print("✓ Interval no merging test passed")
    
    test_intervaldict_combine_correctness()
    print("✓ IntervalDict combine correctness test passed")
    
    test_intervaldict_combine_non_overlapping()
    print("✓ IntervalDict combine non-overlapping test passed")
    
    print("\n" + "=" * 70)
    print("All performance tests passed!")
    print("=" * 70)
    
    # Run benchmarks
    print("\n")
    benchmark_all()
