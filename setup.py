from setuptools import setup

setup(
    name="precalc",
    version="0.1",
    packages=["precalc"],
    install_requires=["numpy", "lmdb", "zarr", "matplotlib", "xarray"],
)
