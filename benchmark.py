#!/usr/bin/env python3
"""
Performance benchmarks comparing Python portion vs Rust portion_rust.

This script benchmarks various interval operations with different numbers
of intervals to demonstrate the performance improvements from the Rust backend.
"""

import random
import time
import statistics
from typing import Callable
import sys

# Pure Python implementation
import portion as P

# Try to import Rust implementation
try:
    import portion_rust as PR
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    print("Warning: portion_rust not available. Install with: cd rust_core && maturin develop --release")
    print()


def benchmark(func: Callable, runs: int = 5, warmup: int = 1) -> tuple[float, float]:
    """Run a benchmark function and return (mean, stdev) in milliseconds."""
    # Warmup runs
    for _ in range(warmup):
        func()

    times = []
    for _ in range(runs):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    return statistics.mean(times), statistics.stdev(times) if len(times) > 1 else 0.0


def create_random_intervals_python(n: int, spread: float = 10000.0) -> P.Interval:
    """Create n random disjoint intervals using Python portion."""
    intervals = P.empty()
    for _ in range(n):
        lower = random.uniform(0, spread)
        upper = lower + random.uniform(0.1, 10.0)
        intervals = intervals | P.closed(lower, upper)
    return intervals


def create_random_intervals_rust(n: int, spread: float = 10000.0):
    """Create n random disjoint intervals using Rust portion_rust."""
    interval = PR.rust_empty()
    for _ in range(n):
        lower = random.uniform(0, spread)
        upper = lower + random.uniform(0.1, 10.0)
        interval = interval | PR.rust_closed(lower, upper)
    return interval


def create_disjoint_intervals_python(n: int) -> P.Interval:
    """Create n clearly disjoint intervals using Python portion."""
    intervals = P.empty()
    for i in range(n):
        intervals = intervals | P.closed(i * 20, i * 20 + 10)
    return intervals


def create_disjoint_intervals_rust(n: int):
    """Create n clearly disjoint intervals using Rust portion_rust."""
    interval = PR.rust_empty()
    for i in range(n):
        interval = interval | PR.rust_closed(i * 20, i * 20 + 10)
    return interval


def print_header(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_result(name: str, py_time: float, py_std: float,
                 rust_time: float | None = None, rust_std: float | None = None):
    """Print a benchmark result with speedup calculation."""
    if rust_time is not None:
        speedup = py_time / rust_time if rust_time > 0 else float('inf')
        print(f"  {name:40} Python: {py_time:8.2f}ms ± {py_std:5.2f}  "
              f"Rust: {rust_time:8.2f}ms ± {rust_std:5.2f}  "
              f"Speedup: {speedup:6.1f}x")
    else:
        print(f"  {name:40} Python: {py_time:8.2f}ms ± {py_std:5.2f}")


def run_benchmarks():
    """Run all benchmarks."""
    print("\n" + "=" * 70)
    print(" PORTION PERFORMANCE BENCHMARK")
    print(" Comparing Pure Python vs Rust Implementation")
    print("=" * 70)

    random.seed(42)  # For reproducibility

    # Benchmark 1: Interval Creation (Union of many intervals)
    print_header("1. INTERVAL CREATION (Union of N intervals)")
    for n in [100, 500, 1000, 5000]:
        random.seed(42)

        def py_create():
            return create_random_intervals_python(n)

        py_mean, py_std = benchmark(py_create, runs=3)

        if RUST_AVAILABLE:
            random.seed(42)

            def rust_create():
                return create_random_intervals_rust(n)

            rust_mean, rust_std = benchmark(rust_create, runs=3)
            print_result(f"Create {n} random intervals", py_mean, py_std, rust_mean, rust_std)
        else:
            print_result(f"Create {n} random intervals", py_mean, py_std)

    # Benchmark 2: Intersection of two large intervals
    print_header("2. INTERSECTION (Two intervals with N atomics each)")
    for n in [100, 500, 1000, 2000]:
        random.seed(42)
        py_a = create_disjoint_intervals_python(n)
        random.seed(43)
        py_b = create_disjoint_intervals_python(n)

        def py_intersection():
            return py_a & py_b

        py_mean, py_std = benchmark(py_intersection, runs=5)

        if RUST_AVAILABLE:
            random.seed(42)
            rust_a = create_disjoint_intervals_rust(n)
            random.seed(43)
            rust_b = create_disjoint_intervals_rust(n)

            def rust_intersection():
                return rust_a & rust_b

            rust_mean, rust_std = benchmark(rust_intersection, runs=5)
            print_result(f"Intersection ({n} atomics each)", py_mean, py_std, rust_mean, rust_std)
        else:
            print_result(f"Intersection ({n} atomics each)", py_mean, py_std)

    # Benchmark 3: Union of two large intervals
    print_header("3. UNION (Two intervals with N atomics each)")
    for n in [100, 500, 1000, 2000]:
        random.seed(42)
        py_a = create_disjoint_intervals_python(n)
        random.seed(43)
        py_b = create_disjoint_intervals_python(n)

        def py_union():
            return py_a | py_b

        py_mean, py_std = benchmark(py_union, runs=5)

        if RUST_AVAILABLE:
            random.seed(42)
            rust_a = create_disjoint_intervals_rust(n)
            random.seed(43)
            rust_b = create_disjoint_intervals_rust(n)

            def rust_union():
                return rust_a | rust_b

            rust_mean, rust_std = benchmark(rust_union, runs=5)
            print_result(f"Union ({n} atomics each)", py_mean, py_std, rust_mean, rust_std)
        else:
            print_result(f"Union ({n} atomics each)", py_mean, py_std)

    # Benchmark 4: Complement
    print_header("4. COMPLEMENT (Interval with N atomics)")
    for n in [100, 500, 1000, 5000]:
        random.seed(42)
        py_interval = create_disjoint_intervals_python(n)

        def py_complement():
            return ~py_interval

        py_mean, py_std = benchmark(py_complement, runs=10)

        if RUST_AVAILABLE:
            random.seed(42)
            rust_interval = create_disjoint_intervals_rust(n)

            def rust_complement():
                return ~rust_interval

            rust_mean, rust_std = benchmark(rust_complement, runs=10)
            print_result(f"Complement ({n} atomics)", py_mean, py_std, rust_mean, rust_std)
        else:
            print_result(f"Complement ({n} atomics)", py_mean, py_std)

    # Benchmark 5: Containment check (value in interval)
    print_header("5. CONTAINMENT CHECK (Value in interval with N atomics)")
    for n in [100, 1000, 5000, 10000]:
        random.seed(42)
        py_interval = create_disjoint_intervals_python(n)
        test_values = [random.uniform(0, n * 20) for _ in range(1000)]

        def py_contains():
            for v in test_values:
                _ = v in py_interval

        py_mean, py_std = benchmark(py_contains, runs=5)

        if RUST_AVAILABLE:
            random.seed(42)
            rust_interval = create_disjoint_intervals_rust(n)

            def rust_contains():
                for v in test_values:
                    _ = v in rust_interval

            rust_mean, rust_std = benchmark(rust_contains, runs=5)
            print_result(f"1000 contains checks ({n} atomics)", py_mean, py_std, rust_mean, rust_std)
        else:
            print_result(f"1000 contains checks ({n} atomics)", py_mean, py_std)

    # Benchmark 6: Difference operation
    print_header("6. DIFFERENCE (A - B with N atomics each)")
    for n in [100, 500, 1000]:
        random.seed(42)
        py_a = create_disjoint_intervals_python(n)
        random.seed(43)
        py_b = create_disjoint_intervals_python(n)

        def py_difference():
            return py_a - py_b

        py_mean, py_std = benchmark(py_difference, runs=3)

        if RUST_AVAILABLE:
            random.seed(42)
            rust_a = create_disjoint_intervals_rust(n)
            random.seed(43)
            rust_b = create_disjoint_intervals_rust(n)

            def rust_difference():
                return rust_a - rust_b

            rust_mean, rust_std = benchmark(rust_difference, runs=3)
            print_result(f"Difference ({n} atomics each)", py_mean, py_std, rust_mean, rust_std)
        else:
            print_result(f"Difference ({n} atomics each)", py_mean, py_std)

    # Benchmark 7: Overlaps check
    print_header("7. OVERLAPS CHECK (Two intervals with N atomics each)")
    for n in [100, 1000, 5000]:
        random.seed(42)
        py_a = create_disjoint_intervals_python(n)
        random.seed(43)
        py_b = create_disjoint_intervals_python(n)

        def py_overlaps():
            for _ in range(100):
                _ = py_a.overlaps(py_b)

        py_mean, py_std = benchmark(py_overlaps, runs=5)

        if RUST_AVAILABLE:
            random.seed(42)
            rust_a = create_disjoint_intervals_rust(n)
            random.seed(43)
            rust_b = create_disjoint_intervals_rust(n)

            def rust_overlaps():
                for _ in range(100):
                    _ = rust_a.overlaps(rust_b)

            rust_mean, rust_std = benchmark(rust_overlaps, runs=5)
            print_result(f"100 overlaps checks ({n} atomics)", py_mean, py_std, rust_mean, rust_std)
        else:
            print_result(f"100 overlaps checks ({n} atomics)", py_mean, py_std)

    # Benchmark 8: Real-world scenario - Many small operations
    print_header("8. REAL-WORLD SCENARIO: Incremental interval building")
    for n in [500, 1000, 2000]:
        random.seed(42)

        def py_scenario():
            intervals = P.empty()
            for i in range(n):
                # Add interval
                intervals = intervals | P.closed(i * 10, i * 10 + 5)
                # Occasionally check containment
                if i % 10 == 0:
                    _ = (i * 10 + 2) in intervals
                # Occasionally do intersection
                if i % 50 == 0:
                    _ = intervals & P.closed(0, i * 5)
            return intervals

        py_mean, py_std = benchmark(py_scenario, runs=3)

        if RUST_AVAILABLE:
            random.seed(42)

            def rust_scenario():
                intervals = PR.rust_empty()
                for i in range(n):
                    # Add interval
                    intervals = intervals | PR.rust_closed(i * 10, i * 10 + 5)
                    # Occasionally check containment
                    if i % 10 == 0:
                        _ = (i * 10 + 2) in intervals
                    # Occasionally do intersection
                    if i % 50 == 0:
                        _ = intervals & PR.rust_closed(0, i * 5)
                return intervals

            rust_mean, rust_std = benchmark(rust_scenario, runs=3)
            print_result(f"Mixed operations ({n} iterations)", py_mean, py_std, rust_mean, rust_std)
        else:
            print_result(f"Mixed operations ({n} iterations)", py_mean, py_std)

    print("\n" + "=" * 70)
    print(" BENCHMARK COMPLETE")
    print("=" * 70)

    if not RUST_AVAILABLE:
        print("\nTo see Rust performance comparisons, install the Rust extension:")
        print("  cd rust_core && maturin develop --release")


if __name__ == "__main__":
    run_benchmarks()
