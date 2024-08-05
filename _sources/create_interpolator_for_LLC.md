---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3.8 (py38)
  language: python
  name: py38
---

# Create interpolator for datasets

```{code-cell} ipython3
import seaduck as sd
import numpy as np
import lmdb
import dask.array as da

import oceanspy as ospy
from precalc.gen_interp import store_interpolator
from precalc.grid_subsample import generate_subocedata
```

So far, we only support interpolator for the LLC4320 dataset. So, first, we load the dataset with the help from oceanspy.

```{code-cell} ipython3
# llc = ospy.open_oceandataset.from_catalog('ECCO')._ds
llc = ospy.open_oceandataset.from_catalog("LLC4320")._ds
```

Now, create the seaduck ocedata object, which is the key for the interpolation. We also need to store the size of the grid into memory for vorticity calculation.

```{code-cell} ipython3
oce = sd.OceData(llc)
oce["dXG"] = np.array(oce["dXG"])
oce["dYG"] = np.array(oce["dYG"])
```

Define how many levels you want to zoom in. Each level will twice as high resolution. Also define, where you want to put the viewer.

```{code-cell} ipython3
zooms = np.arange(7)

lmdb_path = "/home/idies/workspace/Temporary/wenrui/scratch/second_interpolator.lmdb"
env = lmdb.open(lmdb_path, readonly=False, lock=False, map_size=200000000000)
```

For coarse levels, using a fraction of the grid points look exactly the same and it saves some time. That's why we need this subsampling step.

```{code-cell} ipython3
subocedata, unique_grain, inverse_grain = generate_subocedata(zooms, oce)
```

The masking is created by a snapshot of the scalar and velocity data. Variables like HFacC serve the same purpose.

```{code-cell} ipython3
# s = np.array(llc['SALT'][0,0])
# uv = np.array(da.concatenate([llc.UVELMASS[0,0].data[np.newaxis],llc.VVELMASS[0,0].data[np.newaxis]],axis = 0))
s = np.array(llc["S"][0, 0])
uv = np.array(
    da.concatenate([llc.U[0, 0].data[np.newaxis], llc.V[0, 0].data[np.newaxis]], axis=0)
)
```

And this is how you create the interpolator. Go ahead and have all the fun with it!

```{code-cell} ipython3
store_interpolator(
    env, zooms, subocedata, unique_grain, inverse_grain, exmp_vel=uv, exmp_scl=s
)
```
