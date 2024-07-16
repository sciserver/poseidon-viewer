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
import fsspec

combined_velocities = 'file:///home/idies/workspace/poseidon/data01_01/poseidon_viewer/kerchunk/combined_velocities.json'
combined_scalars = 'file:///home/idies/workspace/poseidon/data01_01/poseidon_viewer/kerchunk/combined_scalars.json'
fs_s = fsspec.filesystem('reference', fo=combined_scalars)
fs_v = fsspec.filesystem('reference', fo=combined_velocities)
mapper_v = fs_v.get_mapper('')
mapper_s = fs_s.get_mapper('')

prefix = '/api/values/'
dataset = zarr.open(mapper_s, mode='r')
datasetV = zarr.open(mapper_v, mode='r')
lmdb_path = '/home/idies/workspace/Temporary/wenrui/scratch/first_interpolator.pickle'
env = lmdb.open(lmdb_path, readonly=True, lock=False)

value = '[]'.encode()

def make_scalar_image(read_from,interpolator,varname,itime,idepth,shape = (256,256)):
    weight,ind,inverse = interpolator
    data = np.array(read_from[varname].vindex[(itime,idepth)+tuple(ind.T)])
    value2d = data[inverse]
    # TODO: move this too precalc step
    value2d[value2d == 0.0] = np.nan
    result = np.einsum('ij,ij->i',weight,value2d)
    return result.reshape(shape)

def make_vort_image(read_from,interpolator,itime,idepth,uname = 'U',vname = 'V',shape = (256,256)):
    weight,ind,inverse = interpolator
    # TODO: fix the reading for zarr
    splitter = np.searchsorted(ind[:,0],1)
    data = np.empty(len(ind))
    data[:splitter] = np.array(read_from[uname].vindex[(itime,idepth)+tuple(ind[:splitter,1:].T)])
    data[splitter:] = np.array(read_from[vname].vindex[(itime,idepth)+tuple(ind[splitter:,1:].T)])
    value2d = data[inverse]
    value2d[value2d == 0.0] = np.nan
    du_weight,dv_weight = weight
    result = np.einsum('ij,ij->j',du_weight,value2d[0])+np.einsum('ij,ij->j',dv_weight,value2d[1])
    return result.reshape(shape)

def np_image_from_req(req):
    req_string = req.path
    params = req_string.split('/')[3:]
    variable = params[0]
    if variable == 'velocity':
        # TODO: make the names for vorticity make more sense
        interpolator_type = 'vort'
    else:
        interpolator_type = 'scalar'
        if variable == 'SST':
            variable = 'Theta'
        if variable == 'SSS':
            variable = 'Salt'
    timestamp = params[1]
    zoom = params[2]
    i = params[3]
    j = params[4]
    depth = int(params[5])

    with env.begin(write=False) as txn:
        key=f'{interpolator_type}/{zoom}/{i}/{j}'
        interpolator = pickle.loads(txn.get(key.encode()))

    if interpolator_type == 'vort':
        npimage = make_vort_image(datasetV, interpolator, int(timestamp), depth)
    else:
        npimage = make_scalar_image(dataset, interpolator, variable, int(timestamp), depth)
        
    return npimage

class TileRequestHandler:
    def on_get(self, req, res):
        query = falcon.uri.parse_query_string(req.query_string)
        npimage = np_image_from_req(req)

        normalize = mpl.colors.Normalize(vmin=query['min'], vmax=query['max'])
        colormap = plt.get_cmap(query['colormap'])
        image = Image.fromarray(np.uint8(colormap(normalize(npimage)) * 255))

        with BytesIO() as buffer:
            image.save(buffer, format='png')

            buffer.seek(0)
            res.content_type = 'image/png'
            res.data = buffer.read()

class ColorMapRequestHandler:
    def on_get(self, req, res):
        query = falcon.uri.parse_query_string(req.query_string)
        vmin = float(query['vmin'])
        vmax = float(query['vmax'])
        colormap = query['colormap']
        normalize = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        step = (vmax - vmin) / 255.0
        cmap = plt.get_cmap(colormap)
        a = np.zeros((10, 256))
        for i in range(0, 256):
            a[:,i] = vmin + step*i
        image = Image.fromarray(np.uint8(cmap(normalize(a)) * 255))
        fig, ax = plt.subplots()
        ticks = np.linspace(1,256,8) - 1
        ticklabels = ["{:6.2f}".format(i) for i in (vmin + step*ticks)]
        ax.set_xticks(ticks)
        ax.set_xticklabels(ticklabels)
        ax.set_yticks([])
        plt.imshow(image)
        with BytesIO() as buf:
            plt.savefig(buf, bbox_inches='tight', format='png')
            buf.seek(0)
            res.content_type = 'image/png'
            res.data = buf.read()
        plt.close('all')

class ShapesRequestHandler:
    def on_get(self, req, res):
        res.content_type = 'application/json'
        res.data = value
    def on_post(self, req, res):
        global value
        value = req.bounded_stream.read()

class ValuesRequestHandler:
    def on_get(self, req, res):
        query = falcon.uri.parse_query_string(req.query_string)
        npimage = np_image_from_req(req)

        tile_x=int(query['x'])
        tile_y=int(query['y'])

        res.content_type = 'application/json'
        res.data = ('{"value":'+ str(npimage[tile_y, tile_x]) +'}').encode()


app = falcon.App(cors_enable=True)
app.add_sink(TileRequestHandler().on_get, prefix)
#app.add_sink(InterpolatorRequestHandler().on_get, '/api/interpolators/')
app.add_static_route('/viewer', os.path.abspath('./dist'))
app.add_route('/api/colormap', ColorMapRequestHandler())
app.add_route('/api/shapes', ShapesRequestHandler())
app.add_sink(ValuesRequestHandler().on_get, '/api/val/')

class CustomWSGIRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    port = 8000
    with make_server('', port, app, handler_class=CustomWSGIRequestHandler) as httpd:
        print('Serving on port {}...'.format(port))
        httpd.serve_forever()
