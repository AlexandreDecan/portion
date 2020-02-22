import hypothesis.strategies as st
from hypothesis import assume

import intervals as I


values = st.integers(min_value=-50, max_value=50)
bounds = st.sampled_from([I.CLOSED, I.OPEN])

@st.composite
def closed_intervals(draw, values=values):
    left, right = draw(values), draw(values)
    assume(left < right)
    return I.closed(left, right)

@st.composite
def openclosed_intervals(draw, values=values):
    left, right = draw(values), draw(values)
    assume(left < right)
    return I.openclosed(left, right)

@st.composite
def closedopen_intervals(draw, values=values):
    left, right = draw(values), draw(values)
    assume(left < right)
    return I.closedopen(left, right)

@st.composite
def open_intervals(draw, values=values):
    left, right = draw(values), draw(values)
    assume(left < right)
    return I.open(left, right)

@st.composite
def singleton(draw, values=values):
    return I.singleton(draw(values))

@st.composite
def empty(draw):
    return I.empty()

@st.composite
def atomics(draw, values=values):
    return draw(st.one_of(
        closed_intervals(values),
        openclosed_intervals(values),
        closed_intervals(values),
        open_intervals(values),
        singleton(values),
        empty()
    ))

@st.composite
def intervals(draw, values=values):
    items = draw(st.lists(atomics(values), min_size=1, max_size=10))
    return I.Interval(*items)
