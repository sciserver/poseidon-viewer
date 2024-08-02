# How to use

First down load the tool with git,

```shell
git clone https://github.com/sciserver/poseidon-viewer.git
```

To create the interpolator, simply run the notebook [create_interpolator_for_LLC](create_interpolator_for_LLC).

For functions used in the notebook, documentations are [here](api_reference).

After an interpolator is created, change the path in `render_server.py` to the path you created for the new interpolator, put the it in `~/poseidon-viewer`, and run it with `python render_server.py`
