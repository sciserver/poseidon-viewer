import numpy as np
import warnings
import xarray as xr
import seaduck as sd
from precalc.gen_interp import find_diagnal_index_with_face_vectorized


def subsample_cguv(shape, grain, gshape=None, return_slice=True):
    """Find the index that survive the subsample

    Parameters
    ----------
    shape: int
        The shape of the dataset to subsample
    grain: int
        How many points are going to be represented by one point

    Returns
    -------
    xc,xg: np.ndarray or slice
        index of grid points that survive
    """
    if gshape is None:
        gshape = shape
    if shape % grain != 0:
        warnings.warn(
            "The data size is not divisible by the grain size, "
            "could lead to weird result"
        )
    xc_start = int(np.ceil(grain / 2) - 1)
    if return_slice:
        return slice(xc_start, shape, grain), slice(0, gshape, grain)
    else:
        return np.arange(xc_start, shape, grain), np.arange(0, gshape, grain)


def create_xgyg(oce, grain):
    """Create the new XG,YG location of subset ocedata object"""
    xc = oce.XC
    yc = oce.YC
    xg = oce.XG
    yg = oce.YG
    tp = oce.tp
    cshape = xc.shape
    gshape = xg.shape
    if grain % 2 != 0:
        ixc, ixg = subsample_cguv(cshape[-1], grain, gshape=gshape[-1])
        iyc, iyg = subsample_cguv(cshape[-2], grain, gshape=gshape[-2])
        return xg[:, iyg, ixg], yg[:, iyg, ixg]
    else:
        ixc, ixg = subsample_cguv(
            cshape[-1], grain, gshape=gshape[-1], return_slice=False
        )
        iyc, iyg = subsample_cguv(
            cshape[-2], grain, gshape=gshape[-2], return_slice=False
        )
        if len(cshape) == 3:
            # There is a face dimension
            face = np.arange(cshape[0]).astype(int)
            face, iyg, ixg = np.meshgrid(face, iyg, ixg, indexing="ij")
            the_shape = iyg.shape
            face, iyg, ixg = tuple(i.ravel().astype(int) for i in [face, iyg, ixg])
            nfc, niy, nix = find_diagnal_index_with_face_vectorized(
                face, iyg, ixg, tp, xoffset=-1, yoffset=-1, moves=[1, 2]
            )
            x = xc[nfc, niy, nix]
            y = yc[nfc, niy, nix]
            orig_index = (face, iyg, ixg)
        elif len(cshape) == 2:
            iyg, ixg = np.meshgrid(iyg, ixg, indexing="ij")
            the_shape = iyg.shape
            iyg, ixg = tuple(i.ravel().astype(int) for i in [iyg, ixg])
            niy, nix = tp.ind_tend_vec((iyg, ixg), 1 * np.ones_like(ixg, int))
            niy, nix = tp.ind_tend_vec((niy, nix), 2 * np.ones_like(ixg, int))
            x = xc[niy, nix]
            y = yc[niy, nix]
            orig_index = (iyg, ixg)
        out_of_bound = np.where(niy < 0)
        x[out_of_bound] = xg[orig_index][out_of_bound]
        y[out_of_bound] = yg[orig_index][out_of_bound]
        return x.reshape(the_shape), y.reshape(the_shape)


def subsample_ocedata(oce, grain):
    """Subset an ocedata horizontally and return a new one"""
    small = xr.Dataset()
    shape = oce.XC.shape
    xslc, _ = subsample_cguv(shape[-1], grain)
    yslc, _ = subsample_cguv(shape[-2], grain)
    small["XC"] = xr.DataArray(
        oce._ds["XC"][..., yslc, xslc].data, dims=oce._ds["XC"].dims
    )
    small["YC"] = xr.DataArray(
        oce._ds["YC"][..., yslc, xslc].data, dims=oce._ds["YC"].dims
    )
    xg, yg = create_xgyg(oce, grain)
    if len(shape) == 3:
        small["XG"] = xr.DataArray(xg, dims=("face", "Yp1", "Xp1"))
        small["YG"] = xr.DataArray(yg, dims=("face", "Yp1", "Xp1"))
    else:
        small["XG"] = xr.DataArray(xg, dims=("Yp1", "Xp1"))
        small["YG"] = xr.DataArray(yg, dims=("Yp1", "Xp1"))
    small = sd.OceData(small)
    small["dXG"] = np.array(oce._ds["dxG"][..., yslc, xslc])
    small["dYG"] = np.array(oce._ds["dyG"][..., yslc, xslc])
    return small


def find_common_factors(num1, num2):
    """find all common factors of two numbers"""
    common = []
    g = np.gcd(num1, num2)
    for i in range(1, int(np.sqrt(g)) + 1):
        if g % i == 0:
            common.append(i)
            if g != i * i:
                common.append(g // i)
    return np.array(sorted(common))


def pick_grain_size(zooms, oce, resolution=256, factor=5):
    """Figure out the approprate grain size given zoon levels"""
    rep_dx = np.percentile(oce["dXG"], 90)
    interp_dx = 6371e3 / (2**zooms) / resolution
    h_shape = oce.tp.h_shape
    avail = find_common_factors(h_shape[-2], h_shape[-1])
    avail_dx = avail * rep_dx
    grains = []
    for dx in interp_dx:
        grain_level, interp_res = sd.utils.find_ind(avail_dx, factor * dx, above=False)
        # could add some functions to avoid odd numbers
        grain = avail[grain_level]
        grains.append(grain)
    return grains


def generate_subocedata(zooms, oce, resolution=256):
    """Create the corresponding sd.OceData after coarse-grain defined by zoom levels

    Parameters
    ----------
    zooms: np.ndarray
         numpy array of int for zoom levels
    oce: sd.OceData
        The original dataset
    resolution: number
        The number of point on each face.
    """
    oce["dXG"] = np.array(oce["dXG"])
    oce["dYG"] = np.array(oce["dYG"])
    grains = pick_grain_size(zooms, oce, resolution=resolution)
    unique_grain, inverse_grain = np.unique(grains, return_inverse=True)
    subocedata = []
    for grain in unique_grain:
        print(f"Creating subset of the sd.OceData object with grain size {grain}")
        if grain == 1:
            subocedata.append(oce)
        else:
            subocedata.append(subsample_ocedata(oce, grain))
    return subocedata, unique_grain, inverse_grain
