from wsgiref.simple_server import make_server, WSGIRequestHandler
import falcon
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import zarr
import pickle
import os
import lmdb
import cmocean

prefix = '/api/values/'
dataset = zarr.open('/srv/poseidon/data02_01/LLC4320/2D/SS0', mode='r')
datasetV = zarr.open('/srv/velocity', mode='r')
interpolators_path = '/srv/TileInterpolators'
env = lmdb.open(interpolators_path)

#A class that contains all relevant information to produce a LLC image
class LLC_interp(object):
    def __init__(self,geom, N,M,Proj,b=False):
        self.Proj = Proj
        #resampling_size
        self.N = N
        #pixel_grid_size
        self.M = M
        self.width = M
        if Proj == 'LL':
            self.width = 2*M
        self.height = M
        self.geom = geom
        self.geom_grid = buildInterpGrid(geom,N,b)
        self.pixel_grid = buildPixelGridProj(M,Proj)
        self.weights, self.vertices  = getWeights(self.geom_grid,self.pixel_grid)

class LLC_interp_tile(object):
    def __init__(self, coords, args):
        depthImg = args['dImg']
        w = args['w']
        d = args['dTrace']

        self.x = coords[0]
        self.y = coords[1]
        self.z = coords[2]

        dim = 2**(self.z)
        t = w.M//dim

        image = np.full((w.width,w.height), False, dtype=bool)
        image[t*self.y: t*(self.y+1), t*self.x: t*(self.x+1)] = True
        image = np.ravel(image)

        sMask = np.ravel(depthImg > 0.)
        px = [0,0,0,0]
        self.imMask = [0,0,0,0]

        for k in range(4):
            im = (w.pixel_grid[:,2]==k)&(sMask)
            self.imMask[k] = im[image]
            px[k] = w.pixel_grid[im&image,0:2]

        PMask = [0,0,0,0]

        for k in range(4):
            if px[k].shape != (0,2):
                S = w.geom_grid[k].find_simplex(px[k])
                P = w.geom_grid[k].simplices[S]
                P = np.unique(np.ravel(P))
                PMask[k] = np.zeros(len(w.geom_grid[k].points), dtype=bool)
                PMask[k][P] = True

            else:
                PMask[k] = np.zeros(len(w.geom_grid[k].points), dtype=bool)


        geom_grid = buildInterpGrid(w.geom, w.N, PMask, True)
        self.weights, self.vertices = getWeightsMask(geom_grid, px)

        z0 = geom_grid[0] != None
        z1 = geom_grid[1] != None
        z2 = geom_grid[2] != None
        z3 = geom_grid[3] != None
        self.zones = (z0, z1, z2, z3)


        if np.sum(self.zones) == 0:
            w.coords = None

        else:
            z   = resampleImageTiles(d, w.N)
            Q   = buildImageGridSelect(z, w.N, PMask, self.zones)
            uhash = np.vectorize(unhashp)
            coords = self.tCoords(w.N, PMask, d)

            p = d.values[(coords.T[0], coords.T[1], coords.T[2])]


            for k in range(4):
                if self.zones[k]:
                    vert = np.take(Q[k], self.vertices[k])
                    ind = np.reshape(np.searchsorted(p, np.ravel(vert)), (-1, 3))
                    self.vertices[k] = ind
                else:
                    self.vertices[k] = None

            self.coords = coords


    def tCoords(self, N, MaskP, da):
        z   = resampleImageTiles(da, N)
        Q   = buildImageGridSelect(z, N, MaskP, self.zones)

        uhash = np.vectorize(unhashp)

        wPoints = np.empty(0)
        for k in range(4):
            if self.zones[k]:
                points = np.ravel(np.take(Q[k], self.vertices[k]))
                wPoints = np.concatenate((wPoints, points))

        wPoints = np.unique(wPoints)

        coords = np.row_stack(uhash(wPoints)).T

        return coords

def makeTileFast(dl, param, x, time):
    #-------------------------------
    # resample the image pixels
    #-------------------------------
    if param == 'SST':
        fill = -10
    else:
        fill = 0

    img = np.full(256*256, fill, dtype=np.single)


    if np.sum(x.zones) != 0:
        Q = dl[param].get_coordinate_selection((np.full(x.coords.shape[0], time), x.coords.T[0], x.coords.T[1], x.coords.T[2]))

        for k in range(4):
            if x.zones[k]:
                a = np.einsum('nj,nj->n', np.take(Q, x.vertices[k]), x.weights[k])
                img[x.imMask[k]] = a

        np.nan_to_num(img, copy=False, nan=fill)


    img = np.reshape(img,(256,256))

    if param == 'SST':
        img = (img+10)*1000
    else:
        img = img*1000

    img = img.astype('uint16')
    return img

def makeTileVelocities(dl, x, time, depth):
    fill=0


    imgU = np.full(256*256, fill, dtype=np.single)
    imgV = np.full(256*256, fill, dtype=np.single)



    if np.sum(x.zones) != 0:

        Qu = dl['U'].get_coordinate_selection((np.full(x.coords.shape[0], time), np.full(x.coords.shape[0], depth), x.coords.T[0], x.coords.T[1], x.coords.T[2]))
        Qv = dl['V'].get_coordinate_selection((np.full(x.coords.shape[0], time), np.full(x.coords.shape[0], depth), x.coords.T[0], x.coords.T[1], x.coords.T[2]))

        Qsn = x.sn
        Qcs = x.cs


        #Qsn = dl['SN'].get_coordinate_selection((x.coords.T[0], x.coords.T[1], x.coords.T[2]))
        #Qcs = dl['CS'].get_coordinate_selection((x.coords.T[0], x.coords.T[1], x.coords.T[2]))

        Qur = np.multiply(Qu, Qcs) - np.multiply(Qv, Qsn)
        Qvr = np.multiply(Qu, Qsn) + np.multiply(Qv, Qcs)


        for k in range(4):
            if x.zones[k]:
                a = np.einsum('nj,nj->n', np.take(Qur, x.vertices[k]), x.weights[k])
                imgU[x.imMask[k]] = a

                b = np.einsum('nj,nj->n', np.take(Qvr, x.vertices[k]), x.weights[k])
                imgV[x.imMask[k]] = b

        np.nan_to_num(imgU, copy=False, nan=fill)
        np.nan_to_num(imgV, copy=False, nan=fill)



    imgU = np.reshape(imgU,(256,256))
    imgV = np.reshape(imgV,(256,256))

    imgCurl = np.gradient(imgU, axis=0) - np.gradient(imgV, axis=1)

    imgCurl = np.arcsinh(3*imgCurl)

    imgCurl = (32768*(imgCurl+1)).astype('uint16')

    return imgCurl

class TileRequestHandler:
    def on_get(self, req, res):
        query = falcon.uri.parse_query_string(req.query_string)
        key=req.path[len(prefix):]
        params = key.split('/')
        variable = params[0]
        timestamp = params[1]
        z = params[2]
        x = params[3]
        y = params[4]

        with env.begin(write=False) as txn:
            key='{}/{}/{}'.format(z, x, y)
            interpolator = pickle.loads(txn.get(key.encode()))

        # filename = os.path.join(interpolators_path, 'Z{}/w-{}-{}'.format(z, x, y));
        # with open(filename, 'rb') as f:
        #     interpolator = pickle.load(f)

        if variable == 'velocity':
            depth = int(params[5])
            tile = makeTileVelocities(datasetV, interpolator, int(timestamp), depth)
        else:
            tile = makeTileFast(dataset, variable, interpolator, int(timestamp))

        normalize = mpl.colors.Normalize(vmin=query['min'], vmax=query['max'])
        colormap = plt.get_cmap(query['colormap'])
        image = Image.fromarray(np.uint8(colormap(normalize(tile)) * 255))

        with BytesIO() as buffer:
            image.save(buffer, format='png')
            buffer.seek(0)
            res.content_type = 'image/png'
            res.data = buffer.read()


class InterpolatorRequestHandler:
        def on_get(self, req, res):
                query = falcon.uri.parse_query_string(req.query_string)
                key = req.path[len('/api/interpolators/'):]
                params = key.split('/')
                z = params[0]
                x = params[1]
                y = params[2]

                with env.begin(write=False) as txn:
                        key='{}/{}/{}'.format(z, x, y)
                        interpolator = txn.get(key.encode())

                res.content_type = 'application/octet-stream'
                res.data = interpolator

app = falcon.App()
app.add_sink(TileRequestHandler().on_get, prefix)
app.add_sink(InterpolatorRequestHandler().on_get, '/api/interpolators/')
app.add_static_route('/viewer', os.path.abspath('./dist'))

class CustomWSGIRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    port = 8000
    with make_server('', port, app, handler_class=CustomWSGIRequestHandler) as httpd:
        print('Serving on port {}...'.format(port))
        httpd.serve_forever()
