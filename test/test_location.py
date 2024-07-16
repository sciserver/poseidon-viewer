import seaduck as sd
import pytest
import numpy as np
import dask.array as da
from precalc.gen_interp import (
    lonlat4global_map,
    find_diagnal_index_with_face_vectorized,
    sd_position_from_latlon,
    convert_back,
    weight_index_inverse_from_latlon,
)
from precalc.grid_subsample import subsample_cguv

@pytest.fixture
def xy():
    return lonlat4global_map(1,1,1)

@pytest.fixture
def example_fields():
    ds = sd.utils.get_dataset('ecco')
    s = np.array(ds['SALT'][0,0])
    uv = np.array(da.concatenate([ds.UVELMASS[0,0].data[np.newaxis],ds.VVELMASS[0,0].data[np.newaxis]],axis = 0))
    return s,uv
    
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
@pytest.mark.parametrize(
    "face,iy,ix,ans",
    [
        (np.array([9,11]),np.array([0,2]),np.array([88,0]),
        np.array([[ 3, 10],[ 2,  1],[89, 89]]))
    ]
)
def test_find_diagnal_index_intervene(od,face,iy,ix,ans):
    tp = od.tp
    res = find_diagnal_index_with_face_vectorized(face,iy,ix,tp,
                                                  xoffset = -1,yoffset = -1,
                                                  moves = [1,2],cuvwg = 'C')
    res = np.array(res)
    assert np.allclose(res,ans)
    
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
    ind = np.array([ind])
    old_ind = convert_back(ind,grain,c_or_g)
    xc,xg = subsample_cguv(4320,grain,return_slice = False)
    if c_or_g == 'c':
        use = xc
    else:
        use = xg
    assert use[ind]==old_ind
    
@pytest.mark.parametrize("od",["ecco"], indirect = True)
@pytest.mark.parametrize("grain",[None,1])
@pytest.mark.parametrize("var",['scalar','vort'])
def test_weight_index_inverse_from_latlon(od,xy,example_fields,var,grain):
    lon,lat = xy
    lon = lon.ravel()
    lat = lat.ravel()
    exmp_scl, exmp_vel = example_fields
    weight_index_inverse_from_latlon(od,lat,lon,var = var,grain = grain,exmp_vel = exmp_vel,exmp_scl = exmp_scl)