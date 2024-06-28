import numpy as np
import seaduck as sd
import copy

# def buildWSG84Grid(M):
#     scales = [2**i for i in range(7)]
#     if M/256 not in scales:
#         print('M error')
#         return None,None
    
#     x = np.array(range(M))+0.5
#     y = np.array(range(M))+0.5
    
#     sc = M/(2*math.pi)
#     lon = np.rad2deg(x/sc- math.pi)
#     lat = np.rad2deg(2*(np.arctan(np.exp(math.pi - y/sc))- math.pi/4))
    
#     px,py = np.meshgrid(lon,lat)
    
#     return px,py

scalar_kernel = np.array([
    [0,0],
    [-1,0],
    [0,-1],
    [-1,-1]
])
vortv_kernel = np.array([
    [0,0],
    [-1,0],
])
vortu_kernel = np.array([
    [0,0],
    [0,-1],
])
scalar_knw = sd.KnW(scalar_kernel,inheritance = None)

def lonlat4global_map(zoom,j,i,resolution = 256):
    """Create lat lon points for a subdomain (rendering unit)
    
    Parameters
    ----------
    zoom: int
        The level of zoom it is. Enlarged 2^zoom time compared to zoom=0
    j: int
        Which subdomain in the latitude direction
    i: int
        Which subdomain in the longitudinal direction
    resolution: int
        How many pixels in each direction of the subdomain. 
        
    Returns
    -------
    lon,lat: np.ndarray
        2D arrays of longitude and latitude
    """
    n_zoom = resolution*(2**zoom)
    rescale = 2*np.pi/n_zoom
    x = (np.arange(i*resolution,(i+1)*resolution)+0.5)*rescale
    y = (np.arange(j*resolution,(j+1)*resolution)+0.5)*rescale
    assert (x<2*np.pi).all()
    assert (x>0).all()
    lon = np.rad2deg(x- np.pi)
    lat = np.rad2deg(2*(np.arctan(np.exp(np.pi - y))- np.pi/4))
    return np.meshgrid(lon,lat)

def find_diagnal_index_with_face_vectorized(face,iy,ix,tp,xoffset = 1,yoffset = 1,moves = [0,3]):
    """Find the index for dataset with face connection
    
    Finding the diagnal one involve moving in two directions,
    which is not always straightforward when there is face
    """
    nface,niy,nix = (face,iy+yoffset,ix+xoffset)#naively
    redo = np.where(tp.check_illegal((nface,niy,nix),cuvwg = 'G'))[0]
    for j in redo:
        nface[j],niy[j],nix[j] = tp.ind_moves(
            (face[j],iy[j],ix[j]),
            moves,cuvwg = 'G'
        )
    return nface,niy,nix

def sd_position_from_latlon(lat,lon,ocedata):
    """Create seaduck.Position object for interpolation
    
    Parameters
    ----------
    lat, lon: np.ndarray
        1D array of latitude and longitude
    ocedata: sd.OceData
        Ocean Dataset to perform interpolation
        
    Returns
    -------
    pt: sd.Postion
        The position object, the cornerstone for interpolation,
        The extra indices is index of the closest corner point.
    """
    pt = sd.Position()
    pt = pt.from_latlon(x=lon, y=lat, data=ocedata)
    tp = ocedata.tp
    
    pt.fcg = copy.deepcopy(pt.face)
    pt.iyg = copy.deepcopy(pt.iy)
    pt.ixg = copy.deepcopy(pt.ix)
    pt.ryg = pt.ry+0.5
    pt.rxg = pt.rx+0.5
    # lower_left = np.where(np.logical_and(pt.rx>0,pt.ry<0))
    # points in the lower_left is already taken care of
    
    upper_righ = np.where(np.logical_and(pt.rx>0,pt.ry>0))
    (
        pt.fcg[upper_righ],
        pt.iyg[upper_righ],
        pt.iyg[upper_righ],
    ) = find_diagnal_index_with_face_vectorized(
        pt.fcg[upper_righ],
        pt.iyg[upper_righ],
        pt.iyg[upper_righ],
        tp,
    )
    pt.rxg[upper_righ] = pt.rx[upper_righ]-0.5
    pt.ryg[upper_righ] = pt.ry[upper_righ]-0.5
    
    upper_left = np.where(np.logical_and(pt.rx<0,pt.ry>0))
    (
        pt.fcg[upper_left],
        pt.iyg[upper_left],
        pt.iyg[upper_left],
    ) = tp.ind_tend_vec((
        pt.fcg[upper_left],
        pt.iyg[upper_left],
        pt.iyg[upper_left]),
        0*np.ones(len(upper_left),int),cuvwg = 'G'
    )
    pt.ryg[upper_left] = pt.ry[upper_left]-0.5
    
    lower_righ = np.where(np.logical_and(pt.rx>0,pt.ry<0))
    (
        pt.fcg[lower_righ],
        pt.iyg[lower_righ],
        pt.iyg[lower_righ],
    ) = tp.ind_tend_vec((
        pt.fcg[lower_righ],
        pt.iyg[lower_righ],
        pt.iyg[lower_righ]),
        3*np.ones(len(upper_left),int),cuvwg = 'G'
    )
    pt.rxg[lower_righ] = pt.rx[upper_righ]-0.5
    return pt

def calc_scalar_weight(pt):
    """Thin wrapper aroung sd.utils.weight_f_node
    """
    return sd.utils.weight_f_node(pt.rxg,pt.ryg)

def scalar_data_retrieve(pt,scalar_knw = scalar_knw):
    """Find the indexes to read for the particles
    
    Parameters
    ----------
    pt: sd.Position
        The particle location object
    scalar_knw: sd.KnW
        The kernel object that determines the neighbor points to read. 
        
    Returns
    -------
    uni_ind: np.ndarray
        A 2D array containing all the indices to read
    inverse: np.ndarray
        Unravel the data to construct the interpolation
    """
    # Hack the particle object a bit
    pt.face = pt.fcg
    pt.iy = pt.iyg
    pt.ix = pt.ixg
    nface,niy,nix = pt._fatten_h(scalar_knw)
    ind_shape = nix.shape
    if nface is not None:
        inds = (nface.ravel(),niy.revel(),nix.revel())
    else:
        inds = (niy.revel(),nix.revel())
    inds = np.column_stack(inds)
    uni_ind,inverse = np.unique(inds,axis = 0,return_inverse = True)
    inverse = inverse.reshape(ind_shape)
    return uni_ind, inverse
        