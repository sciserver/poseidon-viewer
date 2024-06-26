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