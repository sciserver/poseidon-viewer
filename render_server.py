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
import fsspec
import cmocean

cmo = cmocean.cm


def make_scalar_image(
    read_from, interpolator, varname, itime, idepth, shape=(256, 256)
):
    """create image from scalar field and interpolator

    Parameters
    ----------
    read_from: zarr dataset or dictionary
        the dataset to be read from
    interpolator: tuple
        output of weight_index_inverse_from_latlon
    varname: string
        key of the variable
    itime: tuple of int
        index of time
    idepth: tuple of int
        index of depth
    shape: tuple of int
        the shape to convert the image back to

    Returns
    -------
    npimage: np.ndarray
        The image to be rendered
    """
    weight, ind, inverse = interpolator
    if varname in ["Eta", "KPPhbl"]:
        data = np.array(read_from[varname].vindex[itime + tuple(ind.T)])
    else:
        data = np.array(read_from[varname].vindex[itime + idepth + tuple(ind.T)])
    if ind[0, 0] == -1:
        data[0] = np.nan
    data[data == 0] = np.nan
    value2d = data[inverse]
    result = np.einsum("ij,ij->i", weight, value2d)
    return result.reshape(shape)


def make_vort_image(
    read_from, interpolator, itime, idepth, uname="U", vname="V", shape=(256, 256)
):
    """create vorticity image from vector field and interpolator

    Parameters
    ----------
    read_from: zarr dataset or dictionary
        the dataset to be read from
    interpolator: tuple
        output of weight_index_inverse_from_latlon
    itime: tuple of int
        index of time
    idepth: tuple of int
        index of depth
    uname: string
        key of the U velocity
    vname: string
        key of the V velocity
    shape: tuple of int
        the shape to convert the image back to

    Returns
    -------
    npimage: np.ndarray
        The image to be rendered
    """
    weight, ind, inverse = interpolator
    inverse, splitter = inverse
    data = np.empty(len(ind))
    data[:splitter] = np.array(
        read_from[uname].vindex[itime + idepth + tuple(ind[:splitter, 1:].T)]
    )
    data[splitter:] = np.array(
        read_from[vname].vindex[itime + idepth + tuple(ind[splitter:, 1:].T)]
    )
    if ind[0, 0] == -1:
        data[0] = np.nan
    data[data == 0] = np.nan
    value2d = data[inverse]
    du_weight, dv_weight = weight
    result = np.einsum("ij,ij->j", du_weight, value2d[0]) + np.einsum(
        "ij,ij->j", dv_weight, value2d[1]
    )
    return result.reshape(shape)


def np_image_from_req(req):
    """Thin wrapper around make_xxx_image functions, parce request"""
    req_string = req.path
    params = req_string.split("/")[3:]
    variable = params[0]
    if variable == "vorticity":
        interpolator_type = "vort"
    else:
        interpolator_type = "scalar"
        if variable == "temperature":
            variable = "Theta"
        if variable == "salinity":
            variable = "Salt"
    timestamp = params[1]
    zoom = params[2]
    i = params[3]
    j = params[4]
    depth = tuple([int(params[5])])

    with env.begin(write=False) as txn:
        key = f"{interpolator_type}/{zoom}/{i}/{j}"
        interpolator = pickle.loads(txn.get(key.encode()))

    if use_filedb:
        itime = tuple([int(timestamp)])
    else:
        it1 = int(timestamp) // 100
        it2 = int(timestamp) % 100
        itime = tuple([it1, it2])

    if interpolator_type == "vort":
        npimage = make_vort_image(datasetV, interpolator, itime, depth)
    else:
        npimage = make_scalar_image(dataset, interpolator, variable, itime, depth)

    return npimage


class TileRequestHandler:
    def on_get(self, req, res):
        query = falcon.uri.parse_query_string(req.query_string)
        npimage = np_image_from_req(req)

        normalize = mpl.colors.Normalize(vmin=query["min"], vmax=query["max"])
        colormap = plt.get_cmap(query["colormap"])
        image = Image.fromarray(np.uint8(colormap(normalize(npimage)) * 255))

        with BytesIO() as buffer:
            image.save(buffer, format="png")

            buffer.seek(0)
            res.content_type = "image/png"
            res.data = buffer.read()


class ColorMapRequestHandler:
    def on_get(self, req, res):
        query = falcon.uri.parse_query_string(req.query_string)
        vmin = float(query["vmin"])
        vmax = float(query["vmax"])
        colormap = query["colormap"]
        normalize = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        step = (vmax - vmin) / 255.0
        cmap = plt.get_cmap(colormap)
        a = np.zeros((10, 256))
        for i in range(0, 256):
            a[:, i] = vmin + step * i
        image = Image.fromarray(np.uint8(cmap(normalize(a)) * 255))
        fig, ax = plt.subplots()
        ticks = np.linspace(1, 256, 8) - 1
        ticklabels = ["{:6.2f}".format(i) for i in (vmin + step * ticks)]
        ax.set_xticks(ticks)
        ax.set_xticklabels(ticklabels)
        ax.set_yticks([])
        plt.imshow(image)
        with BytesIO() as buf:
            plt.savefig(buf, bbox_inches="tight", format="png")
            buf.seek(0)
            res.content_type = "image/png"
            res.data = buf.read()
        plt.close("all")


class ShapesRequestHandler:
    def on_get(self, req, res):
        res.content_type = "application/json"
        res.data = value

    def on_post(self, req, res):
        global value
        value = req.bounded_stream.read()


class ValuesRequestHandler:
    def on_get(self, req, res):
        query = falcon.uri.parse_query_string(req.query_string)
        npimage = np_image_from_req(req)

        tile_x = int(query["x"])
        tile_y = int(query["y"])

        res.content_type = "application/json"
        res.data = ('{"value":' + str(npimage[tile_y, tile_x]) + "}").encode()


class CustomWSGIRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    use_filedb = True
    if use_filedb:
        combined_velocities = "file:///home/idies/workspace/poseidon/data01_01/poseidon_viewer/kerchunk/combined_velocities.json"
        combined_scalars = "file:///home/idies/workspace/poseidon/data01_01/poseidon_viewer/kerchunk/combined_scalars.json"
        fs_s = fsspec.filesystem("reference", fo=combined_scalars)
        fs_v = fsspec.filesystem("reference", fo=combined_velocities)
        mapper_v = fs_v.get_mapper("")
        mapper_s = fs_s.get_mapper("")
        dataset = zarr.open(mapper_s, mode="r")
        datasetV = zarr.open(mapper_v, mode="r")
    else:
        dataset = {}
        datasetV = {}
        for var in ["Salt", "Theta", "W"]:
            dataset[var] = zarr.open(
                f"/home/idies/workspace/poseidon_ceph/LLC4320_subsample/{var}.zarr"
            )[var]
        for var in ["Eta", "KPPhbl"]:
            dataset[var] = zarr.open(
                f"/home/idies/workspace/poseidon_ceph/LLC4320_2d/{var}.zarr"
            )[var]
        for var in ["U", "V"]:
            datasetV[var] = zarr.open(
                f"/home/idies/workspace/poseidon_ceph/LLC4320_subsample/{var}.zarr"
            )[var]

    lmdb_path = "/home/idies/workspace/poseidon/data01_01/poseidon_viewer/TileInterpolators_wenrui/interpolator_12_25.lmdb"
    env = lmdb.open(lmdb_path, readonly=True, lock=False)
    value = "[]".encode()

    app = falcon.App(cors_enable=True)
    app.add_sink(TileRequestHandler().on_get, "/api/values/")
    app.add_static_route("/viewer", os.path.abspath("./dist"))
    app.add_route("/api/colormap", ColorMapRequestHandler())
    app.add_route("/api/shapes", ShapesRequestHandler())
    app.add_sink(ValuesRequestHandler().on_get, "/api/val/")

    port = 8000
    with make_server("", port, app, handler_class=CustomWSGIRequestHandler) as httpd:
        print("Serving on port {}...".format(port))
        httpd.serve_forever()
