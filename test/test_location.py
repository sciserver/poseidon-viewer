import seaduck as sd
import pytest
import numpy as np
from precalc.gen_interp import (
    lonlat4global_map,
    find_diagnal_index_with_face_vectorized,
    sd_position_from_latlon,
)

@pytest.mark.parametrize("j",[0,1])
@pytest.mark.parametrize("i",[0,1])
def test_lonlat4global_map(j,i):
    zoom = 1
    lon,lat = lonlat4global_map(zoom,j,i)
    assert isinstance(lat, np.ndarray)
    assert np.logical_and(lon>-180,lon<180).all()
    
@pytest.mark.parametrize("od",["ecco"], indirect = True)
@pytest.mark.parametrize(
    "face,iy,ix,ans",
    [
        (10,89,45,(2,44,0)),
        (5,45,45,(5,46,46))
    ]
)
def test_find_diagnal_index_with_face_vectorized(od,face,iy,ix,ans):
    tp = od.tp
    face = np.array([face])
    iy = np.array([iy])
    ix = np.array([ix])
    res = find_diagnal_index_with_face_vectorized(face,iy,ix,tp)
    res = tuple(i[0] for i in res)
    assert res==ans
    
    
@pytest.mark.parametrize("od",["ecco"], indirect = True)
def test_create_position(od):
    lon = np.linspace(-50,-30,10)
    pt = sd_position_from_latlon(lon,lon,od)
    assert isinstance(pt, sd.Position)
    assert pt.rxg.dtype == float
    assert pt.iyg.dtype == int
    assert pt.rxg.max()<0.5
    assert pt.rxg.min()>-0.5
    assert pt.ryg.max()<0.5
    assert pt.ryg.min()>-0.5