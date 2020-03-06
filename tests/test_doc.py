import doctest

import portion as P


def test_readme():
    failure = None

    try:
        doctest.testfile('../README.md', raise_on_error=True, globs={'P': P})
    except doctest.DocTestFailure as e:
        failure = e.example.want, e.got, e.example.source

    if failure:
        # Make pytest display it outside the "except" block, to avoid a noisy traceback
        want, got, example = failure
        assert want.strip() == got.strip(), 'DocTest failure in "{}"'.format(example.strip())
        assert False  # In case .strip() removed something useful
