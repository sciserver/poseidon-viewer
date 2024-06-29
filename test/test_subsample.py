import pytest
from precalc.grid_subsample import (
    subsample_cguv,
    convert_back,
    create_xgyg
)

@pytest.mark.parametrize("shape",[90,4320])
@pytest.mark.parametrize("grain",[2,45])
def test_subsample_cguv(shape,grain):
    xc,xg = subsample_cguv(shape,grain,return_slice = False)
    assert len(xc) == shape/grain
    assert len(xg) == shape/grain
    
@pytest.mark.parametrize(
    "ind,grain,c_or_g",
    [
        (0,2,'c'),
        (0,2,'g'),
        (1,4,'c'),
        (0,4,'g'),
        (22,45,'c'),
        (45,45,'g'),
    ]
)
def test_convert_back(ind,grain,c_or_g):
    old_ind = convert_back(ind,grain,c_or_g)
    xc,xg = subsample_cguv(4320,grain,return_slice = False)
    if c_or_g == 'c':
        use = xc
    else:
        use = xg
    assert use[ind]==old_ind
    
@pytest.mark.parametrize("od",["ecco"], indirect = True)
@pytest.mark.parametrize("grain",[2,5,45])
def test_create_xgyg(grain,od):
    xg,yg = create_xgyg(grain,od)
    size_should = 90/grain
    assert (13,size_should,size_should) == xg.shape