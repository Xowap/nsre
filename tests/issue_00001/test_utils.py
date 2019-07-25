from nsre.utils import n_uple


def test_n_uple():
    assert list(n_uple([], n=2)) == []
    assert list(n_uple(range(0, 4), n=2)) == [(0, 1), (1, 2), (2, 3)]
    assert list(n_uple(range(0, 4), n=3)) == [(0, 1, 2), (1, 2, 3)]
