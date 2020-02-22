import doctest

import intervals as I


def test_readme():
    failure = None

    try:
        doctest.testfile('../README.md', raise_on_error=True, globs={'I': I})
    except doctest.DocTestFailure as e:
        failure = e.example.want, e.got, e.example.source

    if failure:
        # Make pytest display it outside the "except" block, to avoid a noisy traceback
        want, got, example = failure
        assert want.strip() == got.strip(), 'DocTest failure in "{}"'.format(example.strip())
        assert False  # In case .strip() removed something useful
