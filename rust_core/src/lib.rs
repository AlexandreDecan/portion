//! High-performance interval operations for Python's portion library.
//!
//! This module provides a Rust implementation of interval arithmetic operations
//! that can be used as a drop-in replacement for the pure Python implementation.

use pyo3::prelude::*;
use pyo3::exceptions::{PyValueError, PyTypeError};
use pyo3::types::PyAny;
use std::cmp::Ordering;
use std::hash::{Hash, Hasher};

/// Represents whether a bound is closed (inclusive) or open (exclusive)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum BoundType {
    Closed,
    Open,
}

impl BoundType {
    #[inline]
    pub fn invert(self) -> BoundType {
        match self {
            BoundType::Closed => BoundType::Open,
            BoundType::Open => BoundType::Closed,
        }
    }
}

/// Represents a value that can be a finite number or infinity
#[derive(Debug, Clone, Copy)]
pub enum Value {
    NegInf,
    Finite(f64),
    PosInf,
}

impl Value {
    #[inline]
    pub fn is_inf(&self) -> bool {
        matches!(self, Value::NegInf | Value::PosInf)
    }
}

impl PartialEq for Value {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Value::NegInf, Value::NegInf) => true,
            (Value::PosInf, Value::PosInf) => true,
            (Value::Finite(a), Value::Finite(b)) => a == b,
            _ => false,
        }
    }
}

impl Eq for Value {}

impl PartialOrd for Value {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Value {
    fn cmp(&self, other: &Self) -> Ordering {
        match (self, other) {
            (Value::NegInf, Value::NegInf) => Ordering::Equal,
            (Value::NegInf, _) => Ordering::Less,
            (_, Value::NegInf) => Ordering::Greater,
            (Value::PosInf, Value::PosInf) => Ordering::Equal,
            (Value::PosInf, _) => Ordering::Greater,
            (_, Value::PosInf) => Ordering::Less,
            (Value::Finite(a), Value::Finite(b)) => a.partial_cmp(b).unwrap_or(Ordering::Equal),
        }
    }
}

impl Hash for Value {
    fn hash<H: Hasher>(&self, state: &mut H) {
        match self {
            Value::NegInf => (-1i64).hash(state),
            Value::PosInf => 1i64.hash(state),
            Value::Finite(v) => v.to_bits().hash(state),
        }
    }
}

/// An atomic interval representing a single contiguous range
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Atomic {
    pub left: BoundType,
    pub lower: Value,
    pub upper: Value,
    pub right: BoundType,
}

impl Atomic {
    pub fn new(left: BoundType, lower: Value, upper: Value, right: BoundType) -> Self {
        // Automatically convert to open bounds when using infinity
        let left = if lower.is_inf() { BoundType::Open } else { left };
        let right = if upper.is_inf() { BoundType::Open } else { right };
        Atomic { left, lower, upper, right }
    }

    /// Check if this atomic interval is empty
    #[inline]
    pub fn is_empty(&self) -> bool {
        match self.lower.cmp(&self.upper) {
            Ordering::Greater => true,
            Ordering::Equal => !(self.left == BoundType::Closed && self.right == BoundType::Closed),
            Ordering::Less => false,
        }
    }

    /// Check if two atomic intervals can be merged (overlap or are adjacent)
    pub fn mergeable(&self, other: &Atomic) -> bool {
        let (first, second) = if self.lower < other.lower
            || (self.lower == other.lower && self.left == BoundType::Closed)
        {
            (self, other)
        } else {
            (other, self)
        };

        if first.upper == second.lower {
            return first.right == BoundType::Closed || second.left == BoundType::Closed;
        }

        first.upper > second.lower
    }

    /// Merge two overlapping or adjacent atomic intervals
    pub fn merge(&self, other: &Atomic) -> Atomic {
        let (lower, left) = if self.lower == other.lower {
            (
                self.lower,
                if self.left == BoundType::Closed {
                    BoundType::Closed
                } else {
                    other.left
                },
            )
        } else if self.lower < other.lower {
            (self.lower, self.left)
        } else {
            (other.lower, other.left)
        };

        let (upper, right) = if self.upper == other.upper {
            (
                self.upper,
                if self.right == BoundType::Closed {
                    BoundType::Closed
                } else {
                    other.right
                },
            )
        } else if self.upper > other.upper {
            (self.upper, self.right)
        } else {
            (other.upper, other.right)
        };

        Atomic::new(left, lower, upper, right)
    }

    /// Compute intersection with another atomic interval
    pub fn intersect(&self, other: &Atomic) -> Option<Atomic> {
        let (lower, left) = if self.lower == other.lower {
            (
                self.lower,
                if self.left == BoundType::Open {
                    BoundType::Open
                } else {
                    other.left
                },
            )
        } else if self.lower > other.lower {
            (self.lower, self.left)
        } else {
            (other.lower, other.left)
        };

        let (upper, right) = if self.upper == other.upper {
            (
                self.upper,
                if self.right == BoundType::Open {
                    BoundType::Open
                } else {
                    other.right
                },
            )
        } else if self.upper < other.upper {
            (self.upper, self.right)
        } else {
            (other.upper, other.right)
        };

        let result = Atomic::new(left, lower, upper, right);
        if result.is_empty() {
            None
        } else {
            Some(result)
        }
    }

    /// Check if this interval is strictly less than another (no overlap)
    #[inline]
    pub fn is_before(&self, other: &Atomic) -> bool {
        if self.right == BoundType::Open || other.left == BoundType::Open {
            self.upper <= other.lower
        } else {
            self.upper < other.lower
        }
    }

    /// Check if this interval contains a value
    #[inline]
    pub fn contains_value(&self, value: Value) -> bool {
        let left_ok = match self.left {
            BoundType::Closed => self.lower <= value,
            BoundType::Open => self.lower < value,
        };
        let right_ok = match self.right {
            BoundType::Closed => value <= self.upper,
            BoundType::Open => value < self.upper,
        };
        left_ok && right_ok
    }

    /// Check if this atomic interval contains another
    pub fn contains_atomic(&self, other: &Atomic) -> bool {
        if other.is_empty() {
            return true;
        }

        let left_ok = other.lower > self.lower
            || (other.lower == self.lower
                && (other.left == self.left || self.left == BoundType::Closed));
        let right_ok = other.upper < self.upper
            || (other.upper == self.upper
                && (other.right == self.right || self.right == BoundType::Closed));

        left_ok && right_ok
    }
}

/// An interval representing a union of atomic intervals
#[derive(Debug, Clone)]
pub struct Interval {
    intervals: Vec<Atomic>,
}

impl Default for Interval {
    fn default() -> Self {
        Interval::empty()
    }
}

impl Interval {
    /// Create an empty interval
    pub fn empty() -> Self {
        Interval { intervals: Vec::new() }
    }

    /// Create an interval from a single atomic interval
    pub fn from_atomic(left: BoundType, lower: Value, upper: Value, right: BoundType) -> Self {
        let atomic = Atomic::new(left, lower, upper, right);
        if atomic.is_empty() {
            Interval::empty()
        } else {
            Interval {
                intervals: vec![atomic],
            }
        }
    }

    /// Create an interval from multiple atomic intervals (with simplification)
    pub fn from_atomics(mut atomics: Vec<Atomic>) -> Self {
        // Filter out empty intervals
        atomics.retain(|a| !a.is_empty());

        if atomics.is_empty() {
            return Interval::empty();
        }

        // Sort by lower bound, closed first
        atomics.sort_by(|a, b| {
            match a.lower.cmp(&b.lower) {
                Ordering::Equal => {
                    // Closed comes before Open
                    match (a.left, b.left) {
                        (BoundType::Closed, BoundType::Open) => Ordering::Less,
                        (BoundType::Open, BoundType::Closed) => Ordering::Greater,
                        _ => Ordering::Equal,
                    }
                }
                other => other,
            }
        });

        // Merge consecutive intervals
        let mut merged: Vec<Atomic> = Vec::with_capacity(atomics.len());
        let mut current = atomics.remove(0);

        for next in atomics {
            if current.mergeable(&next) {
                current = current.merge(&next);
            } else {
                merged.push(current);
                current = next;
            }
        }
        merged.push(current);

        Interval { intervals: merged }
    }

    /// Check if the interval is empty
    #[inline]
    pub fn is_empty(&self) -> bool {
        self.intervals.is_empty()
    }

    /// Check if the interval is atomic (single interval or empty)
    #[inline]
    pub fn is_atomic(&self) -> bool {
        self.intervals.len() <= 1
    }

    /// Get the number of atomic intervals
    #[inline]
    pub fn len(&self) -> usize {
        self.intervals.len()
    }

    /// Get the lower bound of the interval
    pub fn lower(&self) -> Value {
        if self.is_empty() {
            Value::PosInf
        } else {
            self.intervals[0].lower
        }
    }

    /// Get the upper bound of the interval
    pub fn upper(&self) -> Value {
        if self.is_empty() {
            Value::NegInf
        } else {
            self.intervals.last().unwrap().upper
        }
    }

    /// Get the left boundary type
    pub fn left(&self) -> BoundType {
        if self.is_empty() {
            BoundType::Open
        } else {
            self.intervals[0].left
        }
    }

    /// Get the right boundary type
    pub fn right(&self) -> BoundType {
        if self.is_empty() {
            BoundType::Open
        } else {
            self.intervals.last().unwrap().right
        }
    }

    /// Get the enclosure (smallest atomic interval containing this interval)
    pub fn enclosure(&self) -> Interval {
        Interval::from_atomic(self.left(), self.lower(), self.upper(), self.right())
    }

    /// Compute union with another interval
    pub fn union(&self, other: &Interval) -> Interval {
        if self.is_empty() {
            return other.clone();
        }
        if other.is_empty() {
            return self.clone();
        }

        let mut atomics: Vec<Atomic> =
            Vec::with_capacity(self.intervals.len() + other.intervals.len());
        atomics.extend(self.intervals.iter().cloned());
        atomics.extend(other.intervals.iter().cloned());

        Interval::from_atomics(atomics)
    }

    /// Compute intersection with another interval
    pub fn intersection(&self, other: &Interval) -> Interval {
        if self.is_empty() || other.is_empty() {
            return Interval::empty();
        }

        // Early out for non-overlapping intervals
        if self.upper() < other.lower() || self.lower() > other.upper() {
            return Interval::empty();
        }

        // Optimized path for atomic intervals
        if self.is_atomic() && other.is_atomic() {
            if let Some(atomic) = self.intervals[0].intersect(&other.intervals[0]) {
                return Interval { intervals: vec![atomic] };
            } else {
                return Interval::empty();
            }
        }

        let mut intersections: Vec<Atomic> = Vec::new();
        let mut i_iter = self.intervals.iter().peekable();
        let mut o_iter = other.intervals.iter().peekable();

        let mut i_current = i_iter.next();
        let mut o_current = o_iter.next();

        while let (Some(i), Some(o)) = (i_current, o_current) {
            if i.is_before(o) {
                i_current = i_iter.next();
            } else if o.is_before(i) {
                o_current = o_iter.next();
            } else {
                // Overlap exists
                if let Some(intersection) = i.intersect(o) {
                    intersections.push(intersection);
                }

                // Advance the iterator whose interval ends first
                if i.upper < o.upper || (i.upper == o.upper && i.right == BoundType::Open) {
                    i_current = i_iter.next();
                } else if o.upper < i.upper || (i.upper == o.upper && o.right == BoundType::Open) {
                    o_current = o_iter.next();
                } else {
                    i_current = i_iter.next();
                    o_current = o_iter.next();
                }
            }
        }

        if intersections.is_empty() {
            Interval::empty()
        } else {
            Interval { intervals: intersections }
        }
    }

    /// Compute complement of this interval
    pub fn complement(&self) -> Interval {
        if self.is_empty() {
            return Interval::from_atomic(BoundType::Open, Value::NegInf, Value::PosInf, BoundType::Open);
        }

        let mut complements: Vec<Atomic> = Vec::with_capacity(self.intervals.len() + 1);

        // Add (-inf, lower)
        let first = &self.intervals[0];
        let left_complement = Atomic::new(
            BoundType::Open,
            Value::NegInf,
            first.lower,
            first.left.invert(),
        );
        if !left_complement.is_empty() {
            complements.push(left_complement);
        }

        // Add gaps between intervals
        for window in self.intervals.windows(2) {
            let gap = Atomic::new(
                window[0].right.invert(),
                window[0].upper,
                window[1].lower,
                window[1].left.invert(),
            );
            if !gap.is_empty() {
                complements.push(gap);
            }
        }

        // Add (upper, +inf)
        let last = self.intervals.last().unwrap();
        let right_complement = Atomic::new(
            last.right.invert(),
            last.upper,
            Value::PosInf,
            BoundType::Open,
        );
        if !right_complement.is_empty() {
            complements.push(right_complement);
        }

        Interval { intervals: complements }
    }

    /// Compute difference (self - other)
    pub fn difference(&self, other: &Interval) -> Interval {
        self.intersection(&other.complement())
    }

    /// Check if this interval contains a value
    pub fn contains_value(&self, value: Value) -> bool {
        if self.is_empty() {
            return false;
        }

        // Early out
        if self.upper() < value || self.lower() > value {
            return false;
        }

        // Binary search for the containing interval
        let mut low = 0;
        let mut high = self.intervals.len();

        while low < high {
            let mid = (low + high) / 2;
            let current = &self.intervals[mid];

            let before_lower = match current.left {
                BoundType::Open => value <= current.lower,
                BoundType::Closed => value < current.lower,
            };

            if before_lower {
                high = mid;
            } else {
                let after_upper = match current.right {
                    BoundType::Open => value >= current.upper,
                    BoundType::Closed => value > current.upper,
                };

                if after_upper {
                    low = mid + 1;
                } else {
                    return true;
                }
            }
        }

        false
    }

    /// Check if this interval contains another interval
    pub fn contains_interval(&self, other: &Interval) -> bool {
        if other.is_empty() {
            return true;
        }

        if self.is_empty() {
            return false;
        }

        // Early out for non-overlapping intervals
        if self.upper() < other.lower() || self.lower() > other.upper() {
            return false;
        }

        if self.is_atomic() {
            // Check if the single atomic interval contains all of other's intervals
            let self_atomic = &self.intervals[0];
            for other_atomic in &other.intervals {
                if !self_atomic.contains_atomic(other_atomic) {
                    return false;
                }
            }
            return true;
        }

        // For non-atomic self, we need to check each atomic of other
        let mut self_iter = self.intervals.iter();
        let mut current = self_iter.next();

        for other_atomic in &other.intervals {
            // Advance until we find an interval that could contain other_atomic
            while let Some(curr) = current {
                if curr.is_before(other_atomic) {
                    current = self_iter.next();
                } else {
                    break;
                }
            }

            match current {
                Some(curr) => {
                    if !curr.contains_atomic(other_atomic) {
                        return false;
                    }
                }
                None => return false,
            }
        }

        true
    }

    /// Check if two intervals overlap
    pub fn overlaps(&self, other: &Interval) -> bool {
        if self.is_empty() || other.is_empty() {
            return false;
        }

        // Early out for clearly non-overlapping intervals
        if self.upper() < other.lower() || self.lower() > other.upper() {
            return false;
        }

        let mut i_iter = self.intervals.iter();
        let mut o_iter = other.intervals.iter();

        let mut i_current = i_iter.next();
        let mut o_current = o_iter.next();

        while let (Some(i), Some(o)) = (i_current, o_current) {
            if i.is_before(o) {
                i_current = i_iter.next();
            } else if o.is_before(i) {
                o_current = o_iter.next();
            } else {
                return true;
            }
        }

        false
    }

    /// Get iterator over atomic intervals
    pub fn iter(&self) -> impl Iterator<Item = &Atomic> {
        self.intervals.iter()
    }

    /// Get atomic interval at index
    pub fn get(&self, index: usize) -> Option<&Atomic> {
        self.intervals.get(index)
    }
}

impl PartialEq for Interval {
    fn eq(&self, other: &Self) -> bool {
        self.intervals == other.intervals
    }
}

impl Eq for Interval {}

impl Hash for Interval {
    fn hash<H: Hasher>(&self, state: &mut H) {
        for interval in &self.intervals {
            interval.hash(state);
        }
    }
}

// =============================================================================
// Python Bindings
// =============================================================================

/// Python wrapper for BoundType enum
#[pyclass(name = "RustBound")]
#[derive(Clone, Copy)]
pub struct PyBound {
    inner: BoundType,
}

#[pymethods]
impl PyBound {
    #[new]
    fn new(closed: bool) -> Self {
        PyBound {
            inner: if closed { BoundType::Closed } else { BoundType::Open },
        }
    }

    #[staticmethod]
    fn closed() -> Self {
        PyBound { inner: BoundType::Closed }
    }

    #[staticmethod]
    fn open() -> Self {
        PyBound { inner: BoundType::Open }
    }

    fn __invert__(&self) -> Self {
        PyBound { inner: self.inner.invert() }
    }

    fn __eq__(&self, other: &PyBound) -> bool {
        self.inner == other.inner
    }

    fn __repr__(&self) -> String {
        match self.inner {
            BoundType::Closed => "CLOSED".to_string(),
            BoundType::Open => "OPEN".to_string(),
        }
    }

    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }

    #[getter]
    fn is_closed(&self) -> bool {
        self.inner == BoundType::Closed
    }

    #[getter]
    fn is_open(&self) -> bool {
        self.inner == BoundType::Open
    }
}

fn py_to_value(obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    // Check for our special infinity marker
    if let Ok(s) = obj.extract::<String>() {
        if s == "+inf" {
            return Ok(Value::PosInf);
        } else if s == "-inf" {
            return Ok(Value::NegInf);
        }
    }

    // Check for Python's math.inf
    if let Ok(f) = obj.extract::<f64>() {
        if f.is_infinite() {
            return Ok(if f > 0.0 { Value::PosInf } else { Value::NegInf });
        }
        return Ok(Value::Finite(f));
    }

    // Check for int (which can be very large)
    if let Ok(i) = obj.extract::<i64>() {
        return Ok(Value::Finite(i as f64));
    }

    // Check for Python's portion.inf
    let repr = obj.repr()?.to_string();
    if repr.contains("+inf") {
        return Ok(Value::PosInf);
    } else if repr.contains("-inf") {
        return Ok(Value::NegInf);
    }

    Err(PyValueError::new_err(format!(
        "Cannot convert {} to a numeric value",
        repr
    )))
}

fn value_to_py(py: Python<'_>, value: Value) -> PyObject {
    match value {
        Value::NegInf => f64::NEG_INFINITY.to_object(py),
        Value::PosInf => f64::INFINITY.to_object(py),
        Value::Finite(v) => v.to_object(py),
    }
}

fn py_to_bound(obj: &Bound<'_, PyAny>) -> PyResult<BoundType> {
    // Check if it's already a PyBound
    if let Ok(b) = obj.extract::<PyBound>() {
        return Ok(b.inner);
    }

    // Check for bool
    if let Ok(b) = obj.extract::<bool>() {
        return Ok(if b { BoundType::Closed } else { BoundType::Open });
    }

    // Check for string representation
    if let Ok(s) = obj.extract::<String>() {
        let s_lower = s.to_lowercase();
        if s_lower == "closed" || s_lower == "true" {
            return Ok(BoundType::Closed);
        } else if s_lower == "open" || s_lower == "false" {
            return Ok(BoundType::Open);
        }
    }

    // Check repr for portion's Bound
    let repr = obj.repr()?.to_string();
    if repr.contains("CLOSED") {
        return Ok(BoundType::Closed);
    } else if repr.contains("OPEN") {
        return Ok(BoundType::Open);
    }

    Err(PyTypeError::new_err(format!(
        "Cannot convert {} to a Bound",
        repr
    )))
}

/// Python wrapper for Interval
#[pyclass(name = "RustInterval")]
#[derive(Clone)]
pub struct PyInterval {
    pub(crate) inner: Interval,
}

#[pymethods]
impl PyInterval {
    #[new]
    #[pyo3(signature = (*intervals))]
    fn new(intervals: Vec<Bound<'_, PyAny>>) -> PyResult<Self> {
        let mut atomics = Vec::new();

        for interval in intervals {
            if let Ok(py_interval) = interval.extract::<PyInterval>() {
                atomics.extend(py_interval.inner.intervals.clone());
            } else {
                return Err(PyTypeError::new_err(
                    "Arguments must be RustInterval instances",
                ));
            }
        }

        Ok(PyInterval {
            inner: Interval::from_atomics(atomics),
        })
    }

    #[staticmethod]
    fn from_atomic(
        left: Bound<'_, PyAny>,
        lower: Bound<'_, PyAny>,
        upper: Bound<'_, PyAny>,
        right: Bound<'_, PyAny>,
    ) -> PyResult<Self> {
        let left_bound = py_to_bound(&left)?;
        let lower_val = py_to_value(&lower)?;
        let upper_val = py_to_value(&upper)?;
        let right_bound = py_to_bound(&right)?;

        Ok(PyInterval {
            inner: Interval::from_atomic(left_bound, lower_val, upper_val, right_bound),
        })
    }

    #[staticmethod]
    fn empty() -> Self {
        PyInterval {
            inner: Interval::empty(),
        }
    }

    #[getter]
    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    #[getter]
    fn atomic(&self) -> bool {
        self.inner.is_atomic()
    }

    #[getter]
    fn left(&self) -> PyBound {
        PyBound { inner: self.inner.left() }
    }

    #[getter]
    fn right(&self) -> PyBound {
        PyBound { inner: self.inner.right() }
    }

    #[getter]
    fn lower(&self, py: Python<'_>) -> PyObject {
        value_to_py(py, self.inner.lower())
    }

    #[getter]
    fn upper(&self, py: Python<'_>) -> PyObject {
        value_to_py(py, self.inner.upper())
    }

    #[getter]
    fn enclosure(&self) -> Self {
        PyInterval {
            inner: self.inner.enclosure(),
        }
    }

    fn __len__(&self) -> usize {
        self.inner.len()
    }

    fn __and__(&self, other: &PyInterval) -> Self {
        PyInterval {
            inner: self.inner.intersection(&other.inner),
        }
    }

    fn __or__(&self, other: &PyInterval) -> Self {
        PyInterval {
            inner: self.inner.union(&other.inner),
        }
    }

    fn __invert__(&self) -> Self {
        PyInterval {
            inner: self.inner.complement(),
        }
    }

    fn __sub__(&self, other: &PyInterval) -> Self {
        PyInterval {
            inner: self.inner.difference(&other.inner),
        }
    }

    fn __contains__(&self, item: Bound<'_, PyAny>) -> PyResult<bool> {
        if let Ok(interval) = item.extract::<PyInterval>() {
            Ok(self.inner.contains_interval(&interval.inner))
        } else {
            let value = py_to_value(&item)?;
            Ok(self.inner.contains_value(value))
        }
    }

    fn __eq__(&self, other: &PyInterval) -> bool {
        self.inner == other.inner
    }

    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }

    fn __repr__(&self) -> String {
        if self.inner.is_empty() {
            return "()".to_string();
        }

        let parts: Vec<String> = self
            .inner
            .intervals
            .iter()
            .map(|atomic| {
                if atomic.lower == atomic.upper {
                    format!("[{:?}]", atomic.lower)
                } else {
                    let left = if atomic.left == BoundType::Closed { "[" } else { "(" };
                    let right = if atomic.right == BoundType::Closed { "]" } else { ")" };
                    format!("{}{:?},{:?}{}", left, atomic.lower, atomic.upper, right)
                }
            })
            .collect();

        parts.join(" | ")
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyIntervalIter {
        PyIntervalIter {
            inner: slf.inner.clone(),
            index: 0,
        }
    }

    fn __getitem__(&self, index: isize) -> PyResult<Self> {
        let len = self.inner.len() as isize;
        let idx = if index < 0 { len + index } else { index };

        if idx < 0 || idx >= len {
            return Err(pyo3::exceptions::PyIndexError::new_err("index out of range"));
        }

        let atomic = self.inner.intervals[idx as usize].clone();
        Ok(PyInterval {
            inner: Interval { intervals: vec![atomic] },
        })
    }

    fn overlaps(&self, other: &PyInterval) -> bool {
        self.inner.overlaps(&other.inner)
    }

    fn intersection(&self, other: &PyInterval) -> Self {
        self.__and__(other)
    }

    fn union(&self, other: &PyInterval) -> Self {
        self.__or__(other)
    }

    fn complement(&self) -> Self {
        self.__invert__()
    }

    fn difference(&self, other: &PyInterval) -> Self {
        self.__sub__(other)
    }

    fn adjacent(&self, other: &PyInterval) -> bool {
        let intersection = self.inner.intersection(&other.inner);
        let union = self.inner.union(&other.inner);
        intersection.is_empty() && union.is_atomic()
    }

    fn contains(&self, item: Bound<'_, PyAny>) -> PyResult<bool> {
        self.__contains__(item)
    }
}

#[pyclass]
pub struct PyIntervalIter {
    inner: Interval,
    index: usize,
}

#[pymethods]
impl PyIntervalIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(&mut self) -> Option<PyInterval> {
        if self.index < self.inner.len() {
            let atomic = self.inner.intervals[self.index].clone();
            self.index += 1;
            Some(PyInterval {
                inner: Interval { intervals: vec![atomic] },
            })
        } else {
            None
        }
    }
}

// Helper functions exposed to Python
#[pyfunction]
fn rust_open(lower: Bound<'_, PyAny>, upper: Bound<'_, PyAny>) -> PyResult<PyInterval> {
    let lower_val = py_to_value(&lower)?;
    let upper_val = py_to_value(&upper)?;
    Ok(PyInterval {
        inner: Interval::from_atomic(BoundType::Open, lower_val, upper_val, BoundType::Open),
    })
}

#[pyfunction]
fn rust_closed(lower: Bound<'_, PyAny>, upper: Bound<'_, PyAny>) -> PyResult<PyInterval> {
    let lower_val = py_to_value(&lower)?;
    let upper_val = py_to_value(&upper)?;
    Ok(PyInterval {
        inner: Interval::from_atomic(BoundType::Closed, lower_val, upper_val, BoundType::Closed),
    })
}

#[pyfunction]
fn rust_openclosed(lower: Bound<'_, PyAny>, upper: Bound<'_, PyAny>) -> PyResult<PyInterval> {
    let lower_val = py_to_value(&lower)?;
    let upper_val = py_to_value(&upper)?;
    Ok(PyInterval {
        inner: Interval::from_atomic(BoundType::Open, lower_val, upper_val, BoundType::Closed),
    })
}

#[pyfunction]
fn rust_closedopen(lower: Bound<'_, PyAny>, upper: Bound<'_, PyAny>) -> PyResult<PyInterval> {
    let lower_val = py_to_value(&lower)?;
    let upper_val = py_to_value(&upper)?;
    Ok(PyInterval {
        inner: Interval::from_atomic(BoundType::Closed, lower_val, upper_val, BoundType::Open),
    })
}

#[pyfunction]
fn rust_singleton(value: Bound<'_, PyAny>) -> PyResult<PyInterval> {
    let val = py_to_value(&value)?;
    Ok(PyInterval {
        inner: Interval::from_atomic(BoundType::Closed, val, val, BoundType::Closed),
    })
}

#[pyfunction]
fn rust_empty() -> PyInterval {
    PyInterval::empty()
}

/// Python module definition
#[pymodule]
fn portion_rust(m: &Bound<'_, pyo3::types::PyModule>) -> PyResult<()> {
    m.add_class::<PyBound>()?;
    m.add_class::<PyInterval>()?;
    m.add_function(wrap_pyfunction!(rust_open, m)?)?;
    m.add_function(wrap_pyfunction!(rust_closed, m)?)?;
    m.add_function(wrap_pyfunction!(rust_openclosed, m)?)?;
    m.add_function(wrap_pyfunction!(rust_closedopen, m)?)?;
    m.add_function(wrap_pyfunction!(rust_singleton, m)?)?;
    m.add_function(wrap_pyfunction!(rust_empty, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_atomic_empty() {
        let empty = Atomic::new(BoundType::Open, Value::Finite(1.0), Value::Finite(1.0), BoundType::Open);
        assert!(empty.is_empty());

        let not_empty = Atomic::new(BoundType::Closed, Value::Finite(1.0), Value::Finite(1.0), BoundType::Closed);
        assert!(!not_empty.is_empty());
    }

    #[test]
    fn test_atomic_mergeable() {
        let a = Atomic::new(BoundType::Closed, Value::Finite(0.0), Value::Finite(2.0), BoundType::Closed);
        let b = Atomic::new(BoundType::Closed, Value::Finite(2.0), Value::Finite(4.0), BoundType::Closed);
        assert!(a.mergeable(&b));

        let c = Atomic::new(BoundType::Closed, Value::Finite(0.0), Value::Finite(1.0), BoundType::Closed);
        let d = Atomic::new(BoundType::Closed, Value::Finite(3.0), Value::Finite(4.0), BoundType::Closed);
        assert!(!c.mergeable(&d));
    }

    #[test]
    fn test_interval_union() {
        let a = Interval::from_atomic(BoundType::Closed, Value::Finite(0.0), Value::Finite(2.0), BoundType::Closed);
        let b = Interval::from_atomic(BoundType::Closed, Value::Finite(2.0), Value::Finite(4.0), BoundType::Closed);
        let union = a.union(&b);
        assert_eq!(union.len(), 1);
        assert_eq!(union.lower(), Value::Finite(0.0));
        assert_eq!(union.upper(), Value::Finite(4.0));
    }

    #[test]
    fn test_interval_intersection() {
        let a = Interval::from_atomic(BoundType::Closed, Value::Finite(0.0), Value::Finite(3.0), BoundType::Closed);
        let b = Interval::from_atomic(BoundType::Closed, Value::Finite(2.0), Value::Finite(5.0), BoundType::Closed);
        let intersection = a.intersection(&b);
        assert_eq!(intersection.len(), 1);
        assert_eq!(intersection.lower(), Value::Finite(2.0));
        assert_eq!(intersection.upper(), Value::Finite(3.0));
    }

    #[test]
    fn test_interval_complement() {
        let a = Interval::from_atomic(BoundType::Closed, Value::Finite(0.0), Value::Finite(1.0), BoundType::Closed);
        let complement = a.complement();
        assert_eq!(complement.len(), 2);
    }

    #[test]
    fn test_interval_contains() {
        let a = Interval::from_atomic(BoundType::Closed, Value::Finite(0.0), Value::Finite(10.0), BoundType::Closed);
        assert!(a.contains_value(Value::Finite(5.0)));
        assert!(a.contains_value(Value::Finite(0.0)));
        assert!(a.contains_value(Value::Finite(10.0)));
        assert!(!a.contains_value(Value::Finite(-1.0)));
        assert!(!a.contains_value(Value::Finite(11.0)));
    }

    #[test]
    fn test_many_intervals() {
        // Create many disjoint intervals
        let intervals: Vec<Atomic> = (0..1000)
            .map(|i| {
                Atomic::new(
                    BoundType::Closed,
                    Value::Finite(i as f64 * 10.0),
                    Value::Finite(i as f64 * 10.0 + 5.0),
                    BoundType::Closed,
                )
            })
            .collect();

        let interval = Interval::from_atomics(intervals);
        assert_eq!(interval.len(), 1000);

        // Test containment
        assert!(interval.contains_value(Value::Finite(50.0)));
        assert!(!interval.contains_value(Value::Finite(56.0)));
    }
}
