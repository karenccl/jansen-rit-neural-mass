import numpy as np
import pytest

import simulate_jr as m


def test_sigmoid_half_maximum():
    # At v = v0 the firing rate is half its maximum (2 * e0), i.e. e0.
    assert m.sigmoid(m.V0) == pytest.approx(m.E0)


def test_sigmoid_bounds():
    assert m.sigmoid(-1e6) == pytest.approx(0.0)
    assert m.sigmoid(1e6) == pytest.approx(2 * m.E0)


def test_rhs_shape_and_input_entry():
    y = np.zeros(6)
    d0 = np.array(m.rhs(0.0, y, p=0.0))
    d1 = np.array(m.rhs(0.0, y, p=100.0))
    assert d0.shape == (6,)
    # Changing p should alter only dy4 (index 4), by A * a * delta_p.
    diff = d1 - d0
    assert diff[4] == pytest.approx(m.A * m.a * 100.0)
    assert np.allclose(np.delete(diff, 4), 0.0)
