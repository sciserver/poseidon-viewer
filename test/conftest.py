import pytest
import numpy as np
import seaduck as sd
from seaduck import utils


@pytest.fixture(scope="session")
def ds(request):
    return utils.get_dataset(request.param)


@pytest.fixture(scope="session")
def od(request):
    tub = sd.OceData(utils.get_dataset(request.param))
    tub['dXG'] = np.array(tub['dXG'])
    tub['dYG'] = np.array(tub['dYG'])
    return tub


@pytest.fixture(scope="session")
def tp(request):
    return sd.Topology(utils.get_dataset(request.param))