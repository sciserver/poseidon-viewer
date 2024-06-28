import numpy as np
import warnings
from precalc.gen_interp import find_diagnal_index_with_face_vectorized

def subsample_cguv(shape,grain,gshape = None,return_slice = True):
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
    if shape%grain !=0:
        warnings.warn(
            "The data size is not divisible by the grain size, "
            "could lead to weird result"
                    )
    xc_start = np.ceil(grain/2)-1
    if return_slice:
        return slice(xc_start, shape, grain),slice(0, gshape, grain)
    else:
        returdn np.arange(xc_start, shape, grain),np.arange(0, gshape, grain)

def convert_back(ind,grain,c_or_g = 'c'):
    if c_or_g == 'c':
        xc_start = np.ceil(grain/2)-1
    else:
        xc_start = 0
        
    return xc_start+ind*grain

def create_xgyg(grain,xc,yc,xg,yg,tp = None):
    cshape = xc.shape
    gshape = xg.shape
    if grain%2!=0:
        ixc,ixg = subsample_cguv(cshape[-1],grain,gshape = gshape[-1])
        iyc,iyg = subsample_cguv(cshape[-2],grain,gshape = gshape[-2])
        return xg[:,iyg,ixg],yg[:,iyg,ixg]
    else:
        ixc,ixg = subsample_cguv(cshape[-1],grain,gshape = gshape[-1],return_slice = False)
        iyc,iyg = subsample_cguv(cshape[-2],grain,gshape = gshape[-2],return_slice = False)
        if len(cshape)==3:
            # There is a face dimension
            face = np.arange(cshape[0])
            face,iyg,ixg = np.meshgrid(face,iyg,ixg)
            the_shape = iyg.shape
            face,iyg,ixg = tuple(i.ravel() for i in [face,iyg,ixg])
            nfc,niy,nix = find_diagnal_index_with_face_vectorized(
                face,iyg,ixg,tp,xoffset = -1,yoffset = -1,moves = [1,2]
            )
            return xc[nfc,niy,nix].reshape(the_shape),yc[nfc,niy,nix].reshape(the_shape)
        elif len(cshape) ==2:
            iyg,ixg = np.meshgrid(iyg,ixg)
            the_shape = iyg.shape
            iyg,ixg = tuple(i.ravel() for i in [iyg,ixg])
            niy,nix = tp.ind_tend_vec(
                (iyg,ixg),1
            )
            niy,nix = tp.ind_tend_vec(
                (niy,nix),2
            )
            out_of_bound = np.where(niy<0)
            x = xc[niy,nix]
            y = yc[niy,nix]
            x[out_of_bound] = xg[iyg,ixg][out_of_bound]
            y[out_of_bound] = yg[iyg,ixg][out_of_bound]
            return x,y
            