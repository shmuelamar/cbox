from cbox import utils


def test_error2str():
    try:
        raise ValueError('abcd')
    except Exception as e:
        err = e

    strerror = utils.error2str(err)
    assert 'ValueError' in strerror
    assert 'abcd' in strerror
