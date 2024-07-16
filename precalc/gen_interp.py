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

def find_diagnal_index_with_face_vectorized(face,iy,ix,tp,xoffset = 1,yoffset = 1,moves = [0,3],cuvwg = 'G'):
    """Find the index for dataset with face connection
    
    Finding the diagnal one involve moving in two directions,
    which is not always straightforward when there is face
    """
    nface,niy,nix = (copy.deepcopy(face),iy+yoffset,ix+xoffset)#naively
    redo = np.where(tp.check_illegal((nface,niy,nix),cuvwg = cuvwg))[0]
    for j in redo:
        singleuse_moves = copy.deepcopy(moves)
        try:
            nface[j],niy[j],nix[j] = tp.ind_moves(
                (face[j],iy[j],ix[j]),
                singleuse_moves,cuvwg = cuvwg
            )
        except IndexError:
            nface[j],niy[j],nix[j] = -1,-1,-1
    return nface,niy,nix

def fatten_h(pt, knw, ind_moves_kwarg={}):
    """Mirror the Position._fatten_h method in seaduck.

    Fatten means to find the neighboring points of the points of interest based on the kernel.
    faces,iys,ixs are 1d arrays of size n.
    We are applying a kernel of size m.
    This is going to return a n * m array of indexes.
    A very slim vector is now a matrix, and hence the name.
    each row represen all the node needed for interpolation of a single point.
    "h" represent we are only doing it on the horizontal plane.
    This function here is more lenient in the sense that it will return -1 when the index is not legal. 

    Parameters
    ----------
    knw: KnW object
        The kernel used to find neighboring points.
    ind_moves_kward: dict, optional
        Key word argument to put into ind_moves method of the Topology object.
        Read Topology.ind_moves for more detail.
    """
    #         pt.ind_h_dict
    kernel = knw.kernel.astype(int)
    kernel_tends = [sd.eulerian._translate_to_tendency(k) for k in kernel]
    m = len(kernel_tends)
    n = len(pt.iy)
    tp = pt.ocedata.tp

    # the arrays we are going to return
    if pt.face is not None:
        n_faces = np.zeros((n, m), int)
        n_faces.T[:] = pt.face
    n_iys = np.zeros((n, m), int)
    n_ixs = np.zeros((n, m), int)

    # first try to fatten it naively(fast and vectorized)
    for i, node in enumerate(kernel):
        x_disp, y_disp = node
        n_iys[:, i] = pt.iy + y_disp
        n_ixs[:, i] = pt.ix + x_disp
    cuvwg = ind_moves_kwarg.get("cuvwg", "C")
    if pt.face is not None:
        illegal = tp.check_illegal((n_faces, n_iys, n_ixs), cuvwg=cuvwg)
    else:
        illegal = tp.check_illegal((n_iys, n_ixs), cuvwg=cuvwg)

    redo = np.array(np.where(illegal)).T
    for loc in redo:
        j, i = loc
        if pt.face is not None:
            ind = (pt.face[j], pt.iy[j], pt.ix[j])
        else:
            ind = (pt.iy[j], pt.ix[j])
        # everyone start from the [0,0] node
        moves = kernel_tends[i]
        # moves is a list of operations to get to a single point
        # [2,2] means move to the left and then move to the left again.
        try:
            n_ind = tp.ind_moves(ind, moves, **ind_moves_kwarg)
        except IndexError:
            n_ind = tuple(-1 for i in range(len(ind)))
        if pt.face is not None:
            n_faces[j, i], n_iys[j, i], n_ixs[j, i] = n_ind
        else:
            n_iys[j, i], n_ixs[j, i] = n_ind
    if pt.face is not None:
        return n_faces, n_iys, n_ixs
    else:
        return None, n_iys, n_ixs

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
    
    upper_righ = np.where(np.logical_and(pt.rx>0,pt.ry>0))[0]
    (
        pt.fcg[upper_righ],
        pt.iyg[upper_righ],
        pt.ixg[upper_righ],
    ) = find_diagnal_index_with_face_vectorized(
        pt.fcg[upper_righ],
        pt.iyg[upper_righ],
        pt.ixg[upper_righ],
        tp,
    )
    pt.rxg[upper_righ] = pt.rx[upper_righ]-0.5
    pt.ryg[upper_righ] = pt.ry[upper_righ]-0.5
    
    upper_left = np.where(np.logical_and(pt.rx<0,pt.ry>0))[0]
    (
        pt.fcg[upper_left],
        pt.iyg[upper_left],
        pt.ixg[upper_left],
    ) = tp.ind_tend_vec((
        pt.fcg[upper_left],
        pt.iyg[upper_left],
        pt.ixg[upper_left]),
        0*np.ones(len(upper_left),int),cuvwg = 'G'
    )
    pt.ryg[upper_left] = pt.ry[upper_left]-0.5
    
    lower_righ = np.where(np.logical_and(pt.rx>0,pt.ry<0))[0]
    (
        pt.fcg[lower_righ],
        pt.iyg[lower_righ],
        pt.ixg[lower_righ],
    ) = tp.ind_tend_vec((
        pt.fcg[lower_righ],
        pt.iyg[lower_righ],
        pt.ixg[lower_righ]),
        3*np.ones(len(lower_righ),int),cuvwg = 'G'
    )
    pt.rxg[lower_righ] = pt.rx[lower_righ]-0.5
    need_rot = np.where(pt.face!=pt.fcg)[0]
    for i in need_rot:
        edge, new_edge = tp.mutual_direction(
            pt.face[i], pt.fcg[i], transitive=True
        )
        rot = (np.pi - sd.topology.DIRECTIONS[edge] + sd.topology.DIRECTIONS[new_edge]) % (
            np.pi * 2
        )
        pt.rxg[i],pt.ryg[i] = sd.utils.local_to_latlon(pt.rxg[i], pt.ryg[i], np.cos(rot), np.sin(rot))
    return pt

def calc_scalar_weight(pt):
    """Thin wrapper aroung sd.utils.weight_f_node
    """
    weight = sd.utils.weight_f_node(pt.rxg,pt.ryg)[:,[2,3,1,0]]
    iregular = np.where(weight.max(axis = -1)>1.2)
    weight[iregular] = np.array([0.25,0.25,0.25,0.25])
    return weight

def scalar_data_retrieve(pt,scalar_knw = scalar_knw,grain = None,exmp_scl = None):
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
    if exmp_scl is None:
        raise ValueError("need a snapshot of tracer (salinity) for masking")
    # Hack the particle object a bit
    pt.face = pt.fcg
    pt.iy = pt.iyg
    pt.ix = pt.ixg
    nface,niy,nix = fatten_h(pt,scalar_knw)
    ind_shape = nix.shape
    if nface is not None:
        inds = (nface.ravel(),niy.ravel(),nix.ravel())
    else:
        inds = (niy.ravel(),nix.ravel())
    inds = np.column_stack(inds)
    if grain is not None:
        inds[:,-1] = convert_back(inds[:,-1],grain)
        inds[:,-2] = convert_back(inds[:,-2],grain)
    neg = np.where(inds.min(axis = -1)<0)
    inds[neg] = np.array([-1 for i in range(inds.shape[-1])])
    masked = exmp_scl[tuple(inds.T)]==0
    inds[masked] = np.array([-1 for i in range(inds.shape[-1])])
    uni_ind,inverse = np.unique(inds,axis = 0,return_inverse = True)
    inverse = inverse.reshape(ind_shape)
    return uni_ind, inverse

def vort_data_retrieve_with_face(pt,grain = None,exmp_vel = None):
    """Find the indexes to read for the particles
    
    Parameters
    ----------
    pt: sd.Position
        The particle location object
        
    Returns
    -------
    uni_ind: np.ndarray
        A 2D array containing all the indices to read.
        Every row contain information of whether it is u or v
    inverse: np.ndarray
        Unravel the data to construct the interpolation
    """
    # Hack the particle object a bit
    if exmp_vel is None:
        raise ValueError("please give a snapshot of UV for masking")
    tp = pt.ocedata.tp
    inds = []
    rotu = []
    rotv = []
    for component in ['u','v']:
        ufc,uiy,uix = copy.deepcopy((pt.fcg,pt.iyg,pt.ixg))
        if component == 'u':
            uwhich = np.zeros_like(ufc)
            dwhich = np.zeros_like(ufc)
            uiy -= 1
        else:
            uwhich = np.ones_like(ufc)
            dwhich = np.ones_like(ufc)
            uix -= 1
        redo = np.where(tp.check_illegal((ufc,uiy,uix)))[0]
        for j in redo:
            try:
                if component == 'u':
                    which,nind = tp._ind_tend_U((pt.fcg[j],pt.iyg[j],pt.ixg[j]),1)
                    if which == 'V':
                        rotu.append(j)
                else:
                    which,nind = tp._ind_tend_V((pt.fcg[j],pt.iyg[j],pt.ixg[j]),2)
                    if which == 'U':
                        rotv.append(j)
            except IndexError:
                which = 'U',
                nind = (-1,-1,-1)
            if which == 'U':
                uwhich[j] = 0
            else:
                uwhich[j] = 1
            (ufc[j],uiy[j],uix[j]) = nind
        inds.append(([dwhich,uwhich],[pt.fcg,ufc],[pt.iyg,uiy],[pt.ixg,uix]))
    
    inds = np.array(inds).swapaxes(1,0)
    ind_shape = inds[0].shape
    inds = inds.reshape(4,-1).T
    if grain is not None:
        inds = convert_uv_ind_back(inds,grain)
    neg = np.where(inds.min(axis = -1)<0)
    inds[neg] = np.array([-1 for i in range(4)])
    masked = exmp_vel[tuple(inds.T)]==0
    inds[masked] = np.array([-1 for i in range(4)])
    
    uni_ind,inverse = np.unique(inds,axis = 0,return_inverse = True)
    inverse = inverse.reshape(ind_shape)
    return uni_ind, inverse, (rotu,rotv)

def convert_back(ind,grain,c_or_g = 'c'):
    if c_or_g == 'c':
        xc_start = np.ceil(grain/2)-1
    else:
        xc_start = 0
        
    return (xc_start+ind*grain).astype(int)

def convert_uv_ind_back(vinds,grain):
    """Return the original index for UV grid
    """
    is_v = vinds[:,0]
    xc_start = int(np.ceil(grain/2)-1)
    vinds[:,-1]*=grain
    vinds[:,-2]*=grain
    
    vinds[:,-1] += xc_start*is_v
    vinds[:,-2] += xc_start*(1-is_v)
    return vinds

def weight_index_inverse_from_latlon(oce,lat,lon,var = 'scalar',grain = None,exmp_vel = None,exmp_scl = None):
    """Get everything necessary given lat lon and ocedata. 
    """
    pt = sd_position_from_latlon(lat,lon,oce)
    if var == 'scalar':
        weight = calc_scalar_weight(pt)
        ind,inverse = scalar_data_retrieve(pt,grain = grain,exmp_scl = exmp_scl)
        return weight.astype('float32'),ind.astype('int32'),inverse.astype('int32')
    elif var == 'vort':
        ind, inverse, (rotu,rotv) = vort_data_retrieve_with_face(pt,grain = grain,exmp_vel = exmp_vel)
        dx = oce['dXG'][pt.face,pt.iy,pt.ix]
        dy = oce['dYG'][pt.face,pt.iy,pt.ix]
        du_weight = np.ones_like(inverse[0])/dy
        du_weight[0] *= -1 
        du_weight[1,rotu] *= -1
        dv_weight = np.ones_like(inverse[0])/dx
        dv_weight[1] *= -1 
        dv_weight[1,rotv] *= -1
        # TODO: handle dx dy here
        if grain is not None:
            du_weight/=grain
            dv_weight/=grain
        splitter = np.searchsorted(ind[:,0],1)
        return (du_weight.astype('float32'),dv_weight.astype('float32')),ind.astype('int32'),(inverse.astype('int32'),splitter)
    
def store_interpolator(env,zooms,subocedata,unique_grains,inverse_grain,exmp_vel = None,exmp_scl = None):
    with env.begin(write=True) as txn:
        for iz,zoom in enumerate(zooms):
            print(zoom)
            number_of_blocks = int(2**zoom)
            for blck_x in range(number_of_blocks):
                for blck_y in range(number_of_blocks):
                    for var in ['scalar','vort']:
                        key= f'{var}/{zoom}/{blck_x}/{blck_y}'.encode()
                        x,y = lonlat4global_map(zoom,blck_y,blck_x)
                        x = x.ravel()
                        y = y.ravel()
                        sub2use = subocedata[inverse_grain[iz]]
                        grain = unique_grains[inverse_grain[iz]]
                        interpolator = weight_index_inverse_from_latlon(sub2use,y,x,var = var,grain = grain,
                                                                        ,exmp_vel = exmp_vel,exmp_scl = exmp_scl
                                                                       )
                        txn.put(key, pickle.dumps(interpolator))