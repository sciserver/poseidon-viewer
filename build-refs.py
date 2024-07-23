from kerchunk.zarr import single_zarr
from kerchunk.combine import MultiZarrToZarr

prefix = "/srv/poseidon/"
suffix_v = "/llc4320_tests/10dayhourly/velocities"
suffix_s = "/llc4320_tests/10dayhourly/scalars"

combined_velocities = "file:///srv/kerchunk/combined_velocities.json"
combined_scalars = "file:///srv/kerchunk/combined_scalars.json"

refs = []
for node in range(1, 11):
    for dir in range(1, 4):
        path = prefix + f"data{node:02}_{dir:02}" + suffix_v
        refs.append(single_zarr(path))
        print(path)

mz2z = MultiZarrToZarr(refs, remote_protocol="file", xarray_concat_args={"dim": "time"})
mz2z.translate(combined_velocities)

refs = []
for node in range(1, 11):
    for dir in range(1, 4):
        path = prefix + f"data{node:02}_{dir:02}" + suffix_s
        refs.append(single_zarr(path))
        print(path)

mz2z = MultiZarrToZarr(refs, remote_protocol="file", xarray_concat_args={"dim": "time"})
mz2z.translate(combined_scalars)
