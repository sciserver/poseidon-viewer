import pytest
import numpy as np
from precalc.grid_subsample import (
    subsample_cguv,
    create_xgyg,
    generate_subocedata
)

@pytest.mark.parametrize("shape",[90,4320])
@pytest.mark.parametrize("grain",[2,45])
def test_subsample_cguv(shape,grain):
    xc,xg = subsample_cguv(shape,grain,return_slice = False)
    assert len(xc) == shape/grain
    assert len(xg) == shape/grain
    
@pytest.mark.parametrize("od",["ecco"], indirect = True)
@pytest.mark.parametrize("grain",[2,5,45])
def test_create_xgyg(grain,od):
    xg,yg = create_xgyg(od,grain)
    size_should = 90/grain
    assert (13,size_should,size_should) == xg.shape
    
@pytest.mark.parametrize("od",["ecco"], indirect = True)
def test_generate_subocedata(od):
    zooms = np.arange(3)
    generate_subocedata(zooms,od,resolution = 90)