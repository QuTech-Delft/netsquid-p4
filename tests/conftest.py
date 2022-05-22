"""Special pytest file for shared fixtures."""

import pytest
import netsquid


@pytest.fixture
def ns():
    netsquid.sim_reset()
    return netsquid
